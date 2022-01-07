from typing import Optional
from typing import List, Dict

from pydantic import BaseModel

#########################################################################
# Translation
#########################################################################


class EntitySchema(BaseModel):
    text: str
    entity: str


class TranslationInSchema(BaseModel):
    entities: List[EntitySchema] = [
        {"text": "ff a4", "entity": "FORMAT"},
        {"text": "imp 4/4", "entity": "IMPRESSION"},
    ]
    model: str = "imprimeur"


class TranslationOutSchema(BaseModel):
    entities: List[EntitySchema]
