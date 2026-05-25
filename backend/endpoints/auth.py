from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.base import get_db
from backend.database.models import User
from backend.database.schemes import UserLogin, UserRead, UserRegister
from main import app


@app.post("/api/auth/register", response_model=UserRead)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже зарегистрирован")

    new_user = User(
        email=user_data.email.strip().lower(),
        name=user_data.name.strip(),
        delivery_address=user_data.delivery_address.strip(),
        username=user_data.email.strip().lower(),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@app.post("/api/auth/login", response_model=UserRead)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    email = user_data.email.strip().lower()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден. Зарегистрируйтесь")

    return user
