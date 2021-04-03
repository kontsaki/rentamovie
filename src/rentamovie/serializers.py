from fastapi_users.models import BaseUser, BaseUserDB, BaseUserCreate, BaseUserUpdate
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from pydantic import BaseModel

from . import models


class User(BaseUser):
    balance: float = 0


class UserDB(User, BaseUserDB):
    pass


class UserCreate(BaseUserCreate):
    pass


class UserUpdate(User, BaseUserUpdate):
    pass


class MovieID(BaseModel):
    id: int


Movie = pydantic_model_creator(models.Movie, name="Movie")
MovieShortList = pydantic_queryset_creator(
    models.Movie, name="MovieShortList", exclude=("year", "genre")
)
MovieLongList = pydantic_queryset_creator(models.Movie, name="MovieLongList")

Rent = pydantic_model_creator(models.Rent, name="Rent")
