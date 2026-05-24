from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.base import get_db
from backend.database.models import CartItem, MenuItem, Order, OrderItem
from backend.database.schemes import OrderCreate, OrderStatusResponse
from backend.endpoints.cart import get_cart
from main import app

#Оформить заказ
@app.post("/api/cart/{session_id}/checkout")
async def checkout(
        session_id: str,
        order_data: OrderCreate,
        db: AsyncSession = Depends(get_db)
):
    cart = await get_cart(session_id, db)

    if not cart.items:
        raise HTTPException(status_code=400, detail="Корзина пуста")

    new_order = Order(
        user_id=order_data.user_id if order_data.user_id else None,
        session_id=session_id,
        total=cart.total,
        status="pending",
        delivery_address=order_data.delivery_address
    )
    db.add(new_order)
    await db.flush()

    for item in cart.items:
        order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            price_at_time=item.price
        )
        db.add(order_item)

    cart_items = (await db.execute(select(CartItem).where(CartItem.session_id == session_id))).scalars().all()
    for item in cart_items:
        await db.delete(item)

    await db.commit()

    return {
        "message": "Заказ оформлен!",
        "order_id": new_order.id,
        "total": cart.total,
        "status": "pending",
        "estimated_delivery_time": "40 минут"
    }


#Получить статус заказа
@app.get("/api/order/{order_id}/status", response_model=OrderStatusResponse)
async def get_order_status(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    estimated_minutes = None
    if order.status == "pending":
        estimated_minutes = 5
    elif order.status == "cooking":
        estimated_minutes = 25
    elif order.status == "delivering":
        estimated_minutes = 15

    return OrderStatusResponse(
        order_id=order.id,
        status=order.status,
        estimated_time_minutes=estimated_minutes
    )


#Получить детали заказа
@app.get("/api/order/{order_id}")
async def get_order_details(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    items_result = await db.execute(
        select(OrderItem).where(OrderItem.order_id == order_id)
    )
    order_items = items_result.scalars().all()

    items_with_details = []
    for item in order_items:
        menu_result = await db.execute(select(MenuItem).where(MenuItem.id == item.menu_item_id))
        menu_item = menu_result.scalar_one_or_none()

        items_with_details.append({
            "name": menu_item.name if menu_item else "Блюдо удалено",
            "quantity": item.quantity,
            "price": item.price_at_time,
            "total": item.quantity * item.price_at_time
        })

    return {
        "order": order,
        "items": items_with_details
    }