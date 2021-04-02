from fastapi_users.models import BaseUser, BaseUserDB, BaseUserCreate, BaseUserUpdate
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from . import models


class User(BaseUser):
    pass


class UserDB(User, BaseUserDB):
    pass


class UserCreate(BaseUserCreate):
    pass


class UserUpdate(User, BaseUserUpdate):
    pass


Movie = pydantic_model_creator(models.Movie, name="Movie")
MovieList = pydantic_queryset_creator(models.Movie, name="MovieList")
