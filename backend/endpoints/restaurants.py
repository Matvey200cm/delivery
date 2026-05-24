from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.base import get_db
from backend.database.models import MenuItem, Restaurant
from backend.database.schemes import MenuResponse, RestaurantRead, SearchResponse
from main import app

#Получить все рестораны
@app.get("/api/restaurants", response_model=list[RestaurantRead])
async def get_restaurants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Restaurant).where(Restaurant.is_active == True))
    restaurants = result.scalars().all()
    return restaurants


#Поиск блюд и ресторанов
@app.get("/api/search", response_model=SearchResponse)
async def search(query: str = "", db: AsyncSession = Depends(get_db)):
    if not query:
        return SearchResponse(restaurants=[], menu_items=[])

    restaurants_result = await db.execute(
        select(Restaurant).where(Restaurant.name.contains(query))
    )

    menu_result = await db.execute(
        select(MenuItem).where(
            MenuItem.name.contains(query),
            MenuItem.is_available == True
        )
    )

    return SearchResponse(
        restaurants=restaurants_result.scalars().all(),
        menu_items=menu_result.scalars().all(),
    )


#Меню ресторана
@app.get("/api/restaurants/{restaurant_id}/menu", response_model=MenuResponse)
async def get_menu(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MenuItem).where(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.is_available == True
        )
    )
    menu = result.scalars().all()

    if not menu:
        raise HTTPException(status_code=404, detail="Ресторан не найден или меню пусто")

    restaurant_result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    restaurant = restaurant_result.scalar_one_or_none()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Ресторан не найден")

    return MenuResponse(restaurant=restaurant, menu=menu)