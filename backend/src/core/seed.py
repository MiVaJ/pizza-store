import asyncio

from sqlalchemy import select, text

from src.core.database import async_session
from src.models.pizza import Pizza


async def seed_pizzas():
    """Скрипт для первоначального наполнения меню пиццами."""
    async with async_session() as session:
        # Проверка, есть ли уже пиццы в базе, чтобы не дублировать их
        query = select(Pizza)
        result = await session.execute(query)
        if result.scalars().first():
            print("Меню уже содержит пиццы. Сидинг не требуется.")
            return
        
        # Принудительный сброс ID для тестов
        await session.execute(text("ALTER SEQUENCE pizzas_id_seq RESTART WITH 1;"))

        # Стартовый набор пицц
        initial_pizzas = [
            Pizza(
                name="Маргарита",
                description=(
                    "Классический итальянский рецепт: сочные томаты, "
                    "увеличенная порция моцареллы и ароматный базилик."
                ),
                price=45000,
                image_url="https://unsplash.com",
            ),
            Pizza(
                name="Пепперони",
                description=(
                    "Абсолютный хит: пикантные колбаски пепперони, "
                    "моцарелла и фирменный томатный соус."
                ),
                price=55000,
                image_url="https://unsplash.com",
            ),
            Pizza(
                name="Четыре сыра",
                description=(
                    "Изысканное сочетание: моцарелла, пармезан, "
                    "чеддер и нежный сыр с голубой плесенью."
                ),
                price=60000,
                image_url="https://unsplash.com",
            ),
            Pizza(
                name="Мясная",
                description=(
                    "Сытная пицца для любителей мяса: цыпленок, "
                    "острая чоризо, бекон, моцарелла и томатный соус."
                ),
                price=65000,
                image_url="https://unsplash.com",
            ),
            Pizza(
                name="Овощная",
                description=(
                    "Легкий выбор: сладкий перец, томаты, "
                    "красный лук, маслины, кубики брынзы и моцарелла."
                ),
                price=49000,
                image_url="https://unsplash.com",
            ),
        ]

        session.add_all(initial_pizzas)
        await session.commit()
        print("База данных успешно наполнена стартовыми пиццами.")


if __name__ == "__main__":
    asyncio.run(seed_pizzas())
