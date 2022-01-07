from fastapi import Depends, FastAPI
from fastapi.openapi.utils import get_openapi

from fastapi.middleware.cors import (
    CORSMiddleware,
)  #  Cross Origin Resource Sharing (CORS) management

from tortoise import Tortoise  # enable schemas to read relationship between models

from app.database.config import TORTOISE_ORM  # application models config
from app.database.register import register_tortoise

from app.database.models import UserDB
from app.services.users import current_active_user
from app.services.pytorch import load_lang, load_pytorch_checkpoint_inference

from pathlib import Path

import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#########################################################################
# MODELS LOADERS
#########################################################################
# paths
workspace = "datas"
name = "imprimeur"
target = "models"
source = "source"

## PYTORCH
input_lang_name = "imprimerie_brute"
output_lang_name = "imprimerie_normalisee"

PATH_SEQ2SEQ = Path(workspace).joinpath(name, target)
PATH_SEQ2SEQ_MODEL = PATH_SEQ2SEQ.joinpath(
    "seq2seq_imprimerie_brute_imprimerie_normalisee_512_0.001_1641266120_0.00312.dill"
)
seq2seq_input_lang, seq2seq_output_lang = load_lang(
    input_lang_name, output_lang_name, Path(PATH_SEQ2SEQ)
)
seq2seq_encoder, seq2seq_decoder = load_pytorch_checkpoint_inference(
    Path(PATH_SEQ2SEQ_MODEL), seq2seq_input_lang, seq2seq_output_lang, device, 512
)


## TORTOISE
# enable schemas to read relationship between models
Tortoise.init_models(["app.database.models"], "models")

from app.routes import users, products, translation

#########################################################################
# APP
#########################################################################
app = FastAPI()


def my_schema():
    DOCS_TITLE = "Machine Translation API"
    DOCS_VERSION = "1.0"
    openapi_schema = get_openapi(
        title=DOCS_TITLE,
        version=DOCS_VERSION,
        routes=app.routes,
    )
    openapi_schema["info"] = {
        "title": DOCS_TITLE,
        "version": DOCS_VERSION,
        "description": "Sequence 2 Sequence Model with Attention + Named Entities Recognition",
        "contact": {
            "name": "Get Help with this API",
            "url": "https://github.com/vincentporte/machine_translation_fastapi_pytorch_docker/",
            "email": "contact@neuralia.co",
        },
        "license": {
            "name": "GPL-3.0 License ",
            "url": "https://github.com/vincentporte/machine_translation_fastapi_pytorch_docker/blob/main/LICENSE",
        },
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = my_schema

#  Cross Origin Resource Sharing (CORS) management
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, tags=["users"])
app.include_router(products.router, tags=["products"])
app.include_router(translation.router, tags=["translations"])


register_tortoise(app, config=TORTOISE_ORM, generate_schemas=True)


@app.get("/")
async def home():
    return {
        "msg": f"welcome on our character level sequence 2 sequence machine translation demo"
    }


@app.get("/status")
async def health():
    return {"msg": "status up"}
