from fastapi import APIRouter, HTTPException, Path, Body
from typing import List, Dict, Any

router = APIRouter()

dummy_products = [
    {"id": "p1", "name":"Product 1", "price":"1"},
    {"id": "p2", "name":"Product 2", "price":"2"},
    {"id": "p3", "name":"Product 3", "price":"3"}
]

@router.get("/", summary="Gives list of all products")
async def fetch_all_products() -> List[Dict[str, Any]]:
    return {"status":"success", "data":dummy_products}

@router.get("/{product_id}", summary="Get product by Id")
async def fetch_product(product_id:str = Path(...,description="The Id of the product to be fetched")):
    product = next((item for item in dummy_products if item["id"]== product_id), None)
    if product:
        return {"status":"success", "data":product}
    raise HTTPException(status_code=404, detail="Product not found")

@router.post("/", summary="Create a new product")
async def create_product(product_data: Dict[str, Any] = Body(..., example={"name": "New Product", "price": "10"})):
    new_id = f"p{len(dummy_products) + 1}"
    new_product = {"id": new_id, **product_data}
    dummy_products.append(new_product)
    return {"status": "success", "message": "Product created", "product_id": new_id}