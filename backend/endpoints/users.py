from fastapi import *
from select import select
from sqlalchemy.ext.asyncio import *
from backend.database.models import *
from backend.database.schemes import *
from main import app

#Получить всех пользователей
@app.get("/api/users")
async def get_users(db: AsyncSession = Depends()):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


#Создать пользователя
@app.post("/api/users")
async def create_user(user_data: UserCreate, db: AsyncSession = Depends()):
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
async def get_user_orders(user_id: int, db: AsyncSession = Depends()):
    result = await db.execute(
        select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()

    return orders