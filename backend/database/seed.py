from sqlalchemy import select, text

from backend.database.base import Base, async_session_maker, engine
from backend.database.models import MenuItem, Restaurant

RESTAURANTS = [
    ("Пицца плюс", 4.5, 900, "Пицца"),
    ("Тануки", 4.7, 1100, "Пицца и суши"),
    ("FoodBand", 4.4, 800, "Бургеры"),
    ("Жадина-пицца", 4.3, 850, "Пицца"),
    ("Точка еды", 4.6, 1050, "Разное"),
    ("PizzaBurger", 4.8, 750, "Пицца и бургеры"),
]

TANUKI_MENU = [
    ("Ролл угорь стандарт", "Рис, угорь, соус унаги, кунжут, водоросли нори.", 950),
    ("Калифорния лосось", "Рис, лосось, авокадо, огурец, майонез, икра масаго.", 1030),
    ("Окинава стандарт", "Рис, креветка отварная, сыр сливочный, лосось, огурец.", 1250),
    ("Цезарь маки xl", "Рис, куриная грудка копченая, икра масаго, томат.", 900),
    ("Ясай маки стандарт", "Рис, помидор свежий, перец болгарский, авокадо, огурец.", 1050),
    ("Ролл с креветкой стандарт", "Рис, водоросли нори, креветки отварные, сыр сливочный.", 1200),
]

OTHER_MENUS = {
    "Пицца плюс": [
        ("Пепперони", "Томатный соус, моцарелла, пепперони.", 890),
        ("Маргарита", "Томатный соус, моцарелла, базилик.", 750),
    ],
    "FoodBand": [
        ("Чизбургер", "Говяжья котлета, сыр, соус, булка.", 520),
        ("Картофель фри", "Классический картофель фри.", 190),
    ],
    "Жадина-пицца": [
        ("4 сыра", "Моцарелла, пармезан, дор блю, чеддер.", 920),
        ("Грибная", "Шампиньоны, сливочный соус, сыр.", 870),
    ],
    "Точка еды": [
        ("Поке с лососем", "Рис, лосось, авокадо, огурец.", 980),
        ("Салат Цезарь", "Курица, салат, соус, сухарики.", 640),
    ],
    "PizzaBurger": [
        ("Бургер BBQ", "Котлета, бекон, соус BBQ.", 690),
        ("Пицца Мясная", "Ветчина, бекон, пепперони.", 820),
    ],
}


async def sync_tanuki_menu(session) -> None:
    result = await session.execute(select(Restaurant).where(Restaurant.name == "Тануки"))
    tanuki = result.scalar_one_or_none()

    if not tanuki:
        return

    tanuki.rating = 4.7
    tanuki.min_price = 1100
    tanuki.category = "Пицца и суши"

    menu_result = await session.execute(
        select(MenuItem).where(MenuItem.restaurant_id == tanuki.id)
    )
    for item in menu_result.scalars().all():
        await session.delete(item)

    await session.flush()

    for item_name, description, price in TANUKI_MENU:
        session.add(
            MenuItem(
                restaurant_id=tanuki.id,
                name=item_name,
                description=description,
                price=price,
                is_available=True,
            )
        )

    await session.commit()


async def migrate_user_schema() -> None:
    async with engine.begin() as conn:
        result = await conn.execute(text("PRAGMA table_info(users)"))
        columns = {row[1] for row in result.fetchall()}

        if not columns:
            return

        if "email" not in columns:
            await conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(255)"))
        if "name" not in columns:
            await conn.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR(255)"))
        if "delivery_address" not in columns:
            await conn.execute(text("ALTER TABLE users ADD COLUMN delivery_address VARCHAR(500)"))


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await migrate_user_schema()

    async with async_session_maker() as session:
        result = await session.execute(select(Restaurant).limit(1))
        if result.scalar_one_or_none():
            await sync_tanuki_menu(session)
            return

        restaurant_by_name = {}

        for name, rating, min_price, category in RESTAURANTS:
            restaurant = Restaurant(
                name=name,
                rating=rating,
                min_price=min_price,
                category=category,
                is_active=True,
            )
            session.add(restaurant)
            await session.flush()
            restaurant_by_name[name] = restaurant

        tanuki = restaurant_by_name["Тануки"]
        for item_name, description, price in TANUKI_MENU:
            session.add(
                MenuItem(
                    restaurant_id=tanuki.id,
                    name=item_name,
                    description=description,
                    price=price,
                    is_available=True,
                )
            )

        for restaurant_name, menu_items in OTHER_MENUS.items():
            restaurant = restaurant_by_name[restaurant_name]
            for item_name, description, price in menu_items:
                session.add(
                    MenuItem(
                        restaurant_id=restaurant.id,
                        name=item_name,
                        description=description,
                        price=price,
                        is_available=True,
                    )
                )

        await session.commit()
