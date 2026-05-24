from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.base import get_db
from backend.database.models import CartItem, MenuItem, Restaurant
from backend.database.schemes import CartItemResponse, CartResponse
from main import app

#Получить корзину
@app.get("/api/cart/{session_id}", response_model=CartResponse)
async def get_cart(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CartItem).where(CartItem.session_id == session_id)
    )
    cart_items = result.scalars().all()

    items = []
    total = 0

    for cart_item in cart_items:
        menu_result = await db.execute(select(MenuItem).where(MenuItem.id == cart_item.menu_item_id))
        menu_item = menu_result.scalar_one_or_none()

        if menu_item:
            rest_result = await db.execute(select(Restaurant).where(Restaurant.id == menu_item.restaurant_id))
            restaurant = rest_result.scalar_one_or_none()

            items.append(CartItemResponse(
                menu_item_id=menu_item.id,
                name=menu_item.name,
                price=menu_item.price,
                quantity=cart_item.quantity,
                restaurant_id=menu_item.restaurant_id,
                restaurant_name=restaurant.name if restaurant else "Неизвестно"
            ))
            total += menu_item.price * cart_item.quantity

    return CartResponse(session_id=session_id, items=items, total=total)


#Добавить в корзину
@app.post("/api/cart/{session_id}/add/{menu_item_id}")
async def add_to_cart(session_id: str, menu_item_id: int, quantity: int = 1, db: AsyncSession = Depends(get_db)):
    menu_result = await db.execute(select(MenuItem).where(MenuItem.id == menu_item_id))
    menu_item = menu_result.scalar_one_or_none()

    if not menu_item:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")

    result = await db.execute(
        select(CartItem).where(
            CartItem.session_id == session_id,
            CartItem.menu_item_id == menu_item_id
        )
    )
    cart_item = result.scalar_one_or_none()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(session_id=session_id, menu_item_id=menu_item_id, quantity=quantity)
        db.add(cart_item)

    await db.commit()
    return await get_cart(session_id, db)


#Удалить из корзины
@app.delete("/api/cart/{session_id}/remove/{menu_item_id}")
async def remove_from_cart(session_id: str, menu_item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CartItem).where(
            CartItem.session_id == session_id,
            CartItem.menu_item_id == menu_item_id
        )
    )
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Товар не найден в корзине")

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        await db.commit()
    else:
        await db.delete(cart_item)
        await db.commit()

    return await get_cart(session_id, db)


#Очистить корзину
@app.delete("/api/cart/{session_id}/clear")
async def clear_cart(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CartItem).where(CartItem.session_id == session_id)
    )
    cart_items = result.scalars().all()

    for item in cart_items:
        await db.delete(item)

    await db.commit()
    return {"message": "Корзина очищена"}