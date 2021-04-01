from fastapi_users import models
from fastapi_users.db import TortoiseBaseUserModel, TortoiseUserDatabase


class User(models.BaseUser):
    pass


class UserDB(User, models.BaseUserDB):
    pass


class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserModel(TortoiseBaseUserModel):
    pass


user_db = TortoiseUserDatabase(UserDB, UserModel)
