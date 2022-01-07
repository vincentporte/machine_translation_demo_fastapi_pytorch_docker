from fastapi import HTTPException, Depends
from tortoise.exceptions import DoesNotExist

from app.database.models import Product, UserDB, UserModel
from app.schemas.products import ProductInSchema, ProductOutSchema
from app.schemas.status import Status
from app.services.users import current_active_user

from pathlib import Path
from app.main import workspace, name, source


async def get_products():
    return await ProductOutSchema.from_queryset(Product.all())


async def get_product(product_id: int) -> ProductOutSchema:
    return await ProductOutSchema.from_queryset_single(Product.get(id=product_id))


async def create_product(
    product: ProductInSchema, user: UserModel = Depends(current_active_user)
) -> ProductOutSchema:
    product_dict = product.dict(exclude_unset=True)
    product_dict["created_by_id"] = user.id
    product_obj = await Product.create(**product_dict)
    return await ProductOutSchema.from_tortoise_orm(product_obj)


async def update_product(
    product_id: int,
    product: ProductInSchema,
    user: UserModel = Depends(current_active_user),
) -> ProductOutSchema:
    try:
        db_product = await ProductOutSchema.from_queryset_single(
            Product.get(id=product_id)
        )
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

    await Product.filter(id=product_id).update(**product.dict(exclude_unset=True))
    return await ProductOutSchema.from_queryset_single(Product.get(id=product_id))


async def delete_product(product_id) -> Status:
    try:
        db_product = await ProductOutSchema.from_queryset_single(
            Product.get(id=product_id)
        )
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")


async def extract_train():
    extracts = []
    products = await ProductOutSchema.from_queryset(Product.all())

    path_source = Path(workspace).joinpath(name, source)
    path_source.mkdir(parents=True, exist_ok=True)

    MyFile = open(path_source.joinpath("extract.txt"), "w")

    for product in products:
        line = f"{product.entity_type}|{product.source}\t{product.translation}\n"
        MyFile.write(line)

    MyFile.close()

    return {"msg": "extracting"}
