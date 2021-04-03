import os
from typing import Dict, Optional, Union
from datetime import date
from itertools import chain, repeat, islice

from fastapi import FastAPI, Depends, HTTPException
from tortoise import exceptions
from tortoise.contrib.fastapi import register_tortoise
from fastapi_users import FastAPIUsers
from fastapi_users.db import TortoiseUserDatabase

from .authentication import jwt_auth
from . import models, serializers

DATABASE_TYPE = os.environ.get("APP_DATABASE")
DATABASE_URL = f"sqlite://{DATABASE_TYPE}"

app = FastAPI()

fastapi_users = FastAPIUsers(
    TortoiseUserDatabase(serializers.UserDB, models.User),
    [jwt_auth],
    serializers.User,
    serializers.UserCreate,
    serializers.UserUpdate,
    serializers.UserDB,
)

register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={"models": ["rentamovie.models"]},
    generate_schemas=True,
)

app.include_router(
    fastapi_users.get_auth_router(jwt_auth),
    prefix="",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(),
    prefix="",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(),
    prefix="/users",
    tags=["users"],
)

current_user = fastapi_users.current_user()


@app.get("/movies")
async def list_movies(genre: Optional[str] = None, year: Optional[int] = None):
    """List all available for renting movies."""
    query: Dict[str, Union[str, int]] = {}
    if year:
        query["year"] = year
    if genre:
        query["genre"] = genre
    movies_queryset = models.Movie.filter(**query)
    return await serializers.MovieLongList.from_queryset(movies_queryset)


@app.get("/movies/{movie_id}")
async def movie_details(movie_id: int):
    """List all available for renting movies."""
    movie = await models.Movie.get(id=movie_id)
    return await serializers.Movie.from_tortoise_orm(movie)


@app.post("/movies/rent")
async def rent_movie(
    movie: serializers.MovieID, user: serializers.User = Depends(current_user)
):
    """Rent a specific movie."""
    try:
        movie = await models.Movie.get(id=movie.id)
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=400, detail="Movie does not exist.")
    user = await models.User.get(id=user.id)
    try:
        await models.Rent.create(movie=movie, user=user)
    except exceptions.IntegrityError:
        raise HTTPException(status_code=400, detail="Cannot rent same movie twice.")
    return await serializers.Movie.from_tortoise_orm(movie)


@app.get("/users/me/movies")
async def list_rented_movie(user: serializers.User = Depends(current_user)):
    """List movies that have been rented."""
    movies_queryset = models.Movie.filter(rents__user__id=user.id)
    return await serializers.MovieShortList.from_queryset(movies_queryset)


@app.post("/movies/return")
async def return_movie(
    movie: serializers.MovieID, user: serializers.User = Depends(current_user)
):
    """Return a rented movie."""
    movie = await models.Movie.get(id=movie.id)
    user = await models.User.get(id=user.id)
    try:
        rent = await models.Rent.get(movie=movie, user=user)
    except exceptions.DoesNotExist:
        raise HTTPException(status_code=400, detail="This movie was not rented.")

    delta = (date.today() - rent.date).days
    user.balance -= calculate_cost_for(delta or 1)
    await user.save()
    await rent.delete()
    return await serializers.Movie.from_tortoise_orm(movie)


def calculate_cost_for(days):
    charges_per_day = chain(repeat(1.0, 3), repeat(0.5))
    return sum(islice(charges_per_day, 0, days))


@app.get("/movies/cost/{days}")
async def return_cost_estimate(days: int):
    return calculate_cost_for(days)
