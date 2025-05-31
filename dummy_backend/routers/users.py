from fastapi import APIRouter, HTTPException, Path, Body
from typing import Dict, Any

router = APIRouter()

dummy_users = {
    "1": { "id": "1", "name": "Navdeep Singh", "email": "navdeep.s@clear.com"},
    "2": { "id": "2", "name": "John Doe", "email": "john.doe@example.com"},
    "3": { "id": "3", "name": "Jane Smith", "email": "jane.smith@example.com"}
}

@router.get("/", summary="Get all users", description="Retrieve a list of all users")
async def get_all_users():
    print(list(dummy_users.values()))
    return list(dummy_users.values())

@router.get("/{user_id}", summary="Get User by ID")
async def get_user(user_id: str = Path(...,description="The Id of the user to retrive")):
    if user_id not in dummy_users:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status":"success", "data":dummy_users[user_id]}

@router.post("/", summary="Create a New User")
async def create_user(user_data:dict[str, Any] = Body
                      (..., example={"name":"NAVI", "email":"navi@google.com"})):
    new_id = str(len(dummy_users)+1)
    dummy_users[new_id] = {"id":new_id, **user_data}
    return {"status":"success", "message":"User Created", "user_id": new_id}

@router.delete("/{user_id}", summary="Delete User by user_id")
async def delete_user(user_id: str = Path(..., description="The ID of the User to be Deleted")):
    if user_id not in dummy_users:
        raise HTTPException(status_code=404, detail="User not found")
    delete_user = dummy_users.pop(user_id)
    return {"status":"success", "message":f"User {delete_user['name']} deleted"}