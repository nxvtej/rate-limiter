from fastapi import APIRouter, HTTPException, Body, Path
from typing import List, Dict, Any

router = APIRouter()

dummy_orders = [
    {"id":"1", "user_id":"1", "product_id":"p1", "quantity":2, "status":"pending"},
    {"id":"2", "user_id":"2", "product_id":"p2", "quantity":1, "status":"completed"},
    {"id":"3", "user_id":"1", "product_id":"p3", "quantity":3, "status":"shipped"}
]

@router.get("/", summary="Get all orders")
async def get_all_orders() -> List[Dict[str, Any]]:
    return {"status": "success", "data": dummy_orders}

@router.get("/{order_id}", summary="Get order by ID")
async def get_order_by_id(order_id: str = Path(..., description="The ID of the order to fetch")) -> Dict[str, Any]:
    order = next((item for item in dummy_orders if item["id"] == order_id), None)
    if order:
        return {"status": "success", "data": order}
    raise HTTPException(status_code=404, detail="Order not found")

@router.post("/", summary="Create a new order")
async def create_order(order_data: Dict[str, Any] = Body(..., example={"user_id": "1", "product_id": "p1", "quantity": 2})) -> Dict[str, Any]:
    new_id = str(len(dummy_orders) + 1)
    new_order = {"id": new_id, **order_data, "status": "pending"}
    dummy_orders.append(new_order)
    return {"status": "success", "message": "Order created", "order_id": new_id}

@router.put("/{order_id}", summary="Update an existing order")
async def update_order(order_id: str, order_data: Dict[str, Any] = Body(..., example={"quantity": 3, "status": "shipped"})) -> Dict[str, Any]:
    order = next((item for item in dummy_orders if item["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.update(order_data)
    return {"status": "success", "message": "Order updated", "data": order}

@router.delete("/{order_id}", summary="Delete an order")
async def delete_order(order_id: str) -> Dict[str, Any]:
    global dummy_orders
    order = next((item for item in dummy_orders if item["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    dummy_orders = [item for item in dummy_orders if item["id"] != order_id]
    return {"status": "success", "message": "Order deleted"}