from tortoise import fields, models
from tortoise.contrib.pydantic import PydanticModel

from fastapi_users import models as fastapi_users_models
from fastapi_users.db import TortoiseBaseUserModel


######################################################
# USERS Models
######################################################


class User(fastapi_users_models.BaseUser):
    pass


class UserCreate(fastapi_users_models.BaseUserCreate):
    pass


class UserUpdate(fastapi_users_models.BaseUserUpdate):
    pass


class UserModel(TortoiseBaseUserModel):
    pass


class UserDB(User, fastapi_users_models.BaseUserDB, PydanticModel):
    class Config:
        orm_mode = True
        orig_model = UserModel


######################################################
# BUSINESS MODELS
######################################################


class Product(models.Model):
    id = fields.IntField(pk=True)
    entity_type = fields.CharField(max_length=2, default="XX")
    source = fields.CharField(max_length=50, unique=True)
    translation = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    created_by = fields.ForeignKeyField("models.UserModel", related_name="product")
