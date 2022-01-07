from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist, IntegrityError

import app.crud.products as crud
from app.schemas.products import ProductOutSchema, ProductInSchema, UpdateProduct
from app.schemas.status import Status
from app.database.models import UserDB
from app.services.users import current_active_user, current_active_verified_user

router = APIRouter()

#########################################################################
# PRODUCTS database management
#########################################################################


@router.get(
    "/products",
    response_model=List[ProductOutSchema],
    dependencies=[Depends(current_active_user)],
)
async def get_products():
    return await crud.get_products()


@router.get(
    "/product/{product_id}",
    response_model=ProductOutSchema,
    dependencies=[Depends(current_active_user)],
)
async def get_product(product_id: int) -> ProductOutSchema:
    try:
        return await crud.get_product(product_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Product does not exist",
        )


@router.post(
    "/products",
    response_model=ProductOutSchema,
    dependencies=[Depends(current_active_user)],
)
async def create_product(
    product: ProductInSchema, user: UserDB = Depends(current_active_user)
) -> ProductOutSchema:
    try:
        return await crud.create_product(product, user)
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail=f"Product *{product.source}/{product.translation}* already exists",
        )


@router.post(
    "/products/bulk",
    response_model=List[ProductOutSchema],
    dependencies=[Depends(current_active_user)],
)
async def create_product_bulk(
    products: List[ProductInSchema], user: UserDB = Depends(current_active_user)
) -> List[ProductOutSchema]:
    inserted_products = []
    for product in products:
        try:
            inserted_products.append(await crud.create_product(product, user))
        except IntegrityError:
            # replace raise by error log in response
            raise HTTPException(
                status_code=409,
                detail=f"Product *{product.source}/{product.translation} * already exists",
            )

    return inserted_products


@router.patch(
    "/product/{product_id}",
    dependencies=[Depends(current_active_user)],
    response_model=ProductOutSchema,
    responses={404: {"model": HTTPNotFoundError}},
)
async def update_product(product_id: int, product: UpdateProduct) -> ProductOutSchema:
    return await crud.update_product(product_id, product)


@router.delete(
    "/product/{product_id}",
    response_model=Status,
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Depends(current_active_user)],
)
async def delete_product(
    product_id: int,
):
    return await crud.delete_product(product_id)


@router.post(
    "/products/extract",
    response_model=Status,
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Depends(current_active_verified_user)],
)
async def task_extract(user: UserDB = Depends(current_active_user)):
    response = await crud.extract_train()
    return JSONResponse(content=response)
