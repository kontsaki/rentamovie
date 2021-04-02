from fastapi import FastAPI
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


@app.get("/movies")
async def main():
    movies_queryset = models.Movie.all()
    return await serializers.MovieList.from_queryset(movies_queryset)
