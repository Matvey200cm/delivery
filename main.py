# main.py - исправленная версия (без проверки файла)
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi.responses import HTMLResponse
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, func
from sqlalchemy import select

# БАЗА ДАННЫХ
DATABASE_URL = "sqlite+aiosqlite:///./delivery.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


# МОДЕЛИ БД
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    orders = relationship("Order", back_populates="user")


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    rating = Column(Float, default=4.5)
    min_price = Column(Integer, default=900)
    category = Column(String(100))
    is_active = Column(Boolean, default=True)

    menu_items = relationship("MenuItem", back_populates="restaurant")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)

    restaurant = relationship("Restaurant", back_populates="menu_items")
    cart_items = relationship("CartItem", back_populates="menu_item")
    order_items = relationship("OrderItem", back_populates="menu_item")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    menu_item = relationship("MenuItem", back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100))
    status = Column(String(50), default="pending")
    total = Column(Integer, nullable=False)
    delivery_address = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_time = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")


# PYDANTIC СХЕМЫ
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


# ФОНОВЫЕ ЗАДАЧИ
async def update_order_status_background(order_id: int):
    """Фоновая задача: симуляция приготовления и доставки"""
    statuses = [
        ("cooking", 10),
        ("delivering", 25),
        ("delivered", 40)
    ]

    async with async_session_maker() as db:
        for status, delay in statuses:
            await asyncio.sleep(delay)

            result = await db.execute(select(Order).where(Order.id == order_id))
            order = result.scalar_one_or_none()
            if order:
                order.status = status
                if status == "delivered":
                    order.delivered_at = datetime.now()
                await db.commit()


# LIFESPAN ДЛЯ СОЗДАНИЯ ТАБЛИЦ
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        result = await db.execute(select(Restaurant).limit(1))
        if not result.scalar_one_or_none():
            await seed_database(db)

    print("✅ Сервер запущен на http://localhost:8000")
    yield

    await engine.dispose()
    print("🛑 Сервер остановлен")


app = FastAPI(lifespan=lifespan)


# ЗАПОЛНЕНИЕ ТЕСТОВЫМИ ДАННЫМИ
async def seed_database(db: AsyncSession):
    print("📦 Заполняем базу тестовыми данными...")

    restaurants = [
        Restaurant(name="Пицца плюс", rating=4.5, min_price=900, category="Пицца"),
        Restaurant(name="Тануки", rating=4.5, min_price=900, category="Пицца и суши"),
        Restaurant(name="FoodBand", rating=4.3, min_price=850, category="Пицца"),
        Restaurant(name="Жадина-пицца", rating=4.7, min_price=950, category="Пицца"),
        Restaurant(name="Точка еды", rating=4.4, min_price=800, category="Бургеры"),
        Restaurant(name="PizzaBurger", rating=4.6, min_price=1000, category="Пицца и бургеры"),
    ]
    db.add_all(restaurants)
    await db.commit()

    menu_tanuki = [
        MenuItem(restaurant_id=2, name="Ролл угорь стандарт", price=250,
                 description="Рис, угорь, соус унаги, кунжут, водоросли нори"),
        MenuItem(restaurant_id=2, name="Калифорния лосось стандарт", price=395,
                 description="Рис, лосось, авокадо, огурец, майонез, икра масаго, водоросли нори"),
        MenuItem(restaurant_id=2, name="Окинава стандарт", price=250,
                 description="Рис, креветка отварная, сыр сливочный, лосось, огурец свежий"),
        MenuItem(restaurant_id=2, name="Цезарь маки х1", price=250,
                 description="Рис, куриная грудка копченая, икра масаго, томат, айсберг, соус цезарь"),
        MenuItem(restaurant_id=2, name="Ясай маки стандарт", price=250,
                 description="Рис, помидор свежий, перец болгарский, авокадо, огурец, айсберг"),
        MenuItem(restaurant_id=2, name="Ролл с креветкой стандарт", price=250,
                 description="Рис, водоросли нори, креветки отварные, сыр сливочный, огурцы"),
    ]
    db.add_all(menu_tanuki)

    menu_pizza = [
        MenuItem(restaurant_id=1, name="Маргарита", price=450,
                 description="Томатный соус, моцарелла, базилик, оливковое масло"),
        MenuItem(restaurant_id=1, name="Пепперони", price=550,
                 description="Томатный соус, моцарелла, пепперони, орегано"),
        MenuItem(restaurant_id=1, name="Гавайская", price=500,
                 description="Томатный соус, моцарелла, курица, ананас"),
    ]
    db.add_all(menu_pizza)

    users = [
        User(username="Алексей", phone="+7-999-123-45-67"),
        User(username="Мария", phone="+7-999-765-43-21"),
    ]
    db.add_all(users)

    await db.commit()
    print("✅ Тестовые данные загружены!")


# ЭНДПОИНТЫ

@app.get("/")
async def root():
    return {
        "message": "Доставка еды API",
        "version": "4.0",
        "endpoints": {
            "restaurants": "/api/restaurants",
            "search": "/api/search?query=пицца",
            "menu": "/api/restaurants/2/menu",
            "cart": "/api/cart/{session_id}"
        }
    }


# 1. Получить все рестораны
@app.get("/api/restaurants")
async def get_restaurants(db: AsyncSession = Depends()):
    result = await db.execute(select(Restaurant).where(Restaurant.is_active == True))
    restaurants = result.scalars().all()
    return restaurants


# 2. Поиск блюд и ресторанов
@app.get("/api/search")
async def search(query: str = "", db: AsyncSession = Depends()):
    if not query:
        return {"restaurants": [], "menu_items": []}

    restaurants_result = await db.execute(
        select(Restaurant).where(Restaurant.name.contains(query))
    )

    menu_result = await db.execute(
        select(MenuItem).where(
            MenuItem.name.contains(query),
            MenuItem.is_available == True
        )
    )

    return {
        "restaurants": restaurants_result.scalars().all(),
        "menu_items": menu_result.scalars().all()
    }


# 3. Меню ресторана
@app.get("/api/restaurants/{restaurant_id}/menu")
async def get_menu(restaurant_id: int, db: AsyncSession = Depends()):
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

    return {
        "restaurant": restaurant,
        "menu": menu
    }


# 4. Получить корзину
@app.get("/api/cart/{session_id}", response_model=CartResponse)
async def get_cart(session_id: str, db: AsyncSession = Depends()):
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


# 5. Добавить в корзину
@app.post("/api/cart/{session_id}/add/{menu_item_id}")
async def add_to_cart(session_id: str, menu_item_id: int, quantity: int = 1, db: AsyncSession = Depends()):
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


# 6. Удалить из корзины
@app.delete("/api/cart/{session_id}/remove/{menu_item_id}")
async def remove_from_cart(session_id: str, menu_item_id: int, db: AsyncSession = Depends()):
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


# 7. Очистить корзину
@app.delete("/api/cart/{session_id}/clear")
async def clear_cart(session_id: str, db: AsyncSession = Depends()):
    result = await db.execute(
        select(CartItem).where(CartItem.session_id == session_id)
    )
    cart_items = result.scalars().all()

    for item in cart_items:
        await db.delete(item)

    await db.commit()
    return {"message": "Корзина очищена"}


# 8. Оформить заказ
@app.post("/api/cart/{session_id}/checkout")
async def checkout(
        session_id: str,
        order_data: OrderCreate,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends()
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

    background_tasks.add_task(update_order_status_background, new_order.id)

    return {
        "message": "Заказ оформлен!",
        "order_id": new_order.id,
        "total": cart.total,
        "status": "pending",
        "estimated_delivery_time": "40 минут"
    }


# 9. Получить статус заказа
@app.get("/api/order/{order_id}/status", response_model=OrderStatusResponse)
async def get_order_status(order_id: int, db: AsyncSession = Depends()):
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


# 10. Получить детали заказа
@app.get("/api/order/{order_id}")
async def get_order_details(order_id: int, db: AsyncSession = Depends()):
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


# 11. Получить всех пользователей
@app.get("/api/users")
async def get_users(db: AsyncSession = Depends()):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


# 12. Создать пользователя
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


# 13. История заказов пользователя
@app.get("/api/users/{user_id}/orders")
async def get_user_orders(user_id: int, db: AsyncSession = Depends()):
    result = await db.execute(
        select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()

    return orders


# ЗАПУСК
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )