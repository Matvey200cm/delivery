from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.base import get_db
from backend.database.models import User
from backend.database.schemes import AuthLogin, AuthRegister, UserAuthResponse
from main import app


def user_to_auth_response(user: User) -> UserAuthResponse:
    return UserAuthResponse(
        id=user.id,
        name=user.username,
        email=user.phone or "",
        delivery_address=user.delivery_address or "",
    )


@app.post("/api/auth/register", response_model=UserAuthResponse)
async def register(user_data: AuthRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    new_user = User(
        username=user_data.name,
        phone=user_data.email,
        delivery_address=user_data.delivery_address,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return user_to_auth_response(new_user)


@app.post("/api/auth/login", response_model=UserAuthResponse)
async def login(user_data: AuthLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == user_data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user_to_auth_response(user)
