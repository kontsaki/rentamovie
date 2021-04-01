from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from fastapi_users import FastAPIUsers

from .authentication import jwt_auth
from .models import user_db, User, UserCreate, UserUpdate, UserDB

DATABASE_URL = "sqlite://./test.db"

app = FastAPI()

fastapi_users = FastAPIUsers(
    user_db,
    [jwt_auth],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
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


@app.get("/")
async def main():
    return
