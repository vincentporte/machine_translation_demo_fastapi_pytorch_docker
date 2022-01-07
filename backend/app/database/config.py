from decouple import config

DATABASE_URL = config("DATABASE_URL")

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.database.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}

SECRET_KEY = config("SECRET_KEY")
