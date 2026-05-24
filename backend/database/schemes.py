from typing import *
from pydantic import *


class UserCreate(BaseModel):
    username: str
    phone: Optional[str] = None


class CartItemResponse(BaseModel):
    menu_item_id: int
    name: str
    price: int
    quantity: int
    restaurant_id: int
    restaurant_name: str


class CartResponse(BaseModel):
    session_id: str
    items: List[CartItemResponse] = []
    total: int = 0


class OrderCreate(BaseModel):
    delivery_address: str
    user_id: Optional[int] = None


class OrderStatusResponse(BaseModel):
    order_id: int
    status: str
    estimated_time_minutes: Optional[int] = None