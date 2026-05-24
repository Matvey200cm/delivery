from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.base import get_db
from backend.database.models import Order, User
from backend.database.schemes import UserCreate
from main import app

#Получить всех пользователей
@app.get("/api/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


#Создать пользователя
@app.post("/api/users")
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")

    new_user = User(username=user_data.username, phone=user_data.phone)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


#История заказов пользователя
@app.get("/api/users/{user_id}/orders")
async def get_user_orders(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()

    return orders