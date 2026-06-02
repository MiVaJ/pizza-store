import asyncio

from sqlalchemy import text

from src.core.database import async_session
from src.models.ingredient import Ingredient
from src.models.pizza import Pizza


async def seed_pizzas():
    """Скрипт для первоначального наполнения меню пиццами."""
    async with async_session() as session:
        # Полная очистка таблиц перед Сидингом
        await session.execute(
            text(
                """
                TRUNCATE TABLE 
                    pizzas, 
                    ingredients, 
                    pizza_ingredients 
                RESTART IDENTITY CASCADE;
                """
            )
        )
        await session.commit()

        # Стартовый набор соусов
        sauces = [
            Ingredient(
                name="Фирменный томатный",
                price=4000,
                image_url="https://unsplash.com",
                is_sauce=True,
            ),
            Ingredient(
                name="Чесночный (Ранч)",
                price=4000,
                image_url="https://unsplash.com",
                is_sauce=True,
            ),
            Ingredient(
                name="Сырный соус",
                price=4500,
                image_url="https://unsplash.com",
                is_sauce=True,
            ),
            Ingredient(
                name="Барбекю (BBQ)",
                price=4000,
                image_url="https://unsplash.com",
                is_sauce=True,
            ),
        ]
        session.add_all(sauces)
        await session.flush()

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
        print("База данных успешно наполнена стартовыми пиццами и соусами.")


if __name__ == "__main__":
    asyncio.run(seed_pizzas())
