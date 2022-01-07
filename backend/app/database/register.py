from typing import Optional

from tortoise import Tortoise

# Users adaptater
from fastapi_users.db import TortoiseUserDatabase
from app.database.models import UserDB, UserModel


def register_tortoise(
    app,
    config: Optional[dict] = None,
    generate_schemas: bool = False,
) -> None:
    @app.on_event("startup")
    async def init_orm():
        await Tortoise.init(config=config)
        if generate_schemas:
            await Tortoise.generate_schemas()

    @app.on_event("shutdown")
    async def close_orm():
        await Tortoise.close_connections()


async def get_user_db():
    yield TortoiseUserDatabase(UserDB, UserModel)
