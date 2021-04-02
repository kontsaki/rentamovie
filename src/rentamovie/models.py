from enum import Enum

from fastapi_users.db import TortoiseBaseUserModel
from tortoise.models import Model
from tortoise import fields


class User(TortoiseBaseUserModel):
    pass


class Movie(Model):
    title = fields.CharField(max_length=100)
    year = fields.IntField()
    genre = fields.CharField(max_length=10)
