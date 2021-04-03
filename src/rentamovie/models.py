from datetime import date

from fastapi_users.db import TortoiseBaseUserModel
from tortoise.models import Model
from tortoise import fields


class User(TortoiseBaseUserModel):
    balance = fields.FloatField(default=0.0)


class Movie(Model):
    title = fields.CharField(max_length=100)
    year = fields.IntField()
    genre = fields.CharField(max_length=10)


class Rent(Model):
    user = fields.ForeignKeyField("models.User")
    movie = fields.ForeignKeyField("models.Movie")
    date = fields.DateField(default=date.today)

    class Meta:
        unique_together = (("user", "movie"),)
