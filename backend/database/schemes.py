from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class RestaurantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    rating: float
    min_price: int
    category: Optional[str] = None
    is_active: bool = True


class MenuItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    restaurant_id: int
    name: str
    description: Optional[str] = None
    price: int
    is_available: bool = True


class MenuResponse(BaseModel):
    restaurant: RestaurantRead
    menu: List[MenuItemRead]


class SearchResponse(BaseModel):
    restaurants: List[RestaurantRead]
    menu_items: List[MenuItemRead]


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