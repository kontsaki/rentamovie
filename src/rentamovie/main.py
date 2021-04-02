from typing import Dict, Optional, Union

from fastapi import FastAPI, Depends
from tortoise.contrib.fastapi import register_tortoise
from fastapi_users import FastAPIUsers
from fastapi_users.db import TortoiseUserDatabase

from .authentication import jwt_auth
from . import models, serializers

DATABASE_URL = "sqlite://:memory:"

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
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(),
    prefix="/auth",
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
    return await serializers.MovieList.from_queryset(movies_queryset)


@app.get("/movies/{movie_id}")
async def movie_details(movie_id: int):
    """List all available for renting movies."""
    movie = await models.Movie.get(id=movie_id)
    return await serializers.Movie.from_tortoise_orm(movie)


@app.post("/movies/rent/")
async def rent_movie(
    movie: serializers.Movie, user: serializers.User = Depends(current_user)  # type: ignore
):
    """Rent a specific movie."""
    movie = await models.Movie.get(id=movie.id)  # type: ignore
    user = await models.User.get(id=user.id)
    await models.Rent.create(movie=movie, user=user)
    return await serializers.Movie.from_tortoise_orm(movie)


@app.get("/me/movies")
async def list_rented_movie(user: serializers.User = Depends(current_user)):
    """List movies that have been rent."""
    movies_queryset = models.Movie.filter(rents__user__id=user.id)
    return await serializers.MovieList.from_queryset(movies_queryset)
