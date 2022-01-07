from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist, IntegrityError

import app.crud.translation as crud
from app.schemas.translation import TranslationInSchema, TranslationOutSchema
from app.schemas.status import Status

# from app.database.models import UserDB
from app.services.users import current_active_user

router = APIRouter()


@router.post(
    "/translate",
    response_model=TranslationOutSchema,
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Depends(current_active_user)],
)
async def translate(entities: TranslationInSchema) -> TranslationOutSchema:
    return await crud.translate_entities(entities)
