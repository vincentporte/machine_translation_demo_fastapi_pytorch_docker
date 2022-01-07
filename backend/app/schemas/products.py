from typing import Optional
from typing import List, Dict

from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from app.database.models import Product

#########################################################################
# PRODUCTS saved in database
#########################################################################

ProductInSchema = pydantic_model_creator(
    Product,
    name="ProductIn",
    exclude=["created_at", "modified_at", "created_by_id"],
    exclude_readonly=True,
)

ProductOutSchema = pydantic_model_creator(
    Product,
    name="ProductOut",
    exclude=["created_at", "modified_at", "created_by", "created_by_id"],
)


class UpdateProduct(BaseModel):
    source: Optional[str]
    translation: Optional[str]
