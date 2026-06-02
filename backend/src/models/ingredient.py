from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.pizza import Pizza


class PizzaIngredient(Base):
    """Промежуточная таблица между Пиццами и Ингредиентами/Соусами."""

    __tablename__ = "pizza_ingredients"

    pizza_id: Mapped[int] = mapped_column(
        ForeignKey("pizzas.id", ondelete="CASCADE"), primary_key=True
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True
    )


class Ingredient(Base):
    """Модель для хранения соусов и дополнительных ингредиентов."""

    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)

    # True — это соус, False — топпинг пиццы
    is_sauce: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Отношение к пиццам через таблицу связи
    pizzas: Mapped[list["Pizza"]] = relationship(
        secondary="pizza_ingredients", back_populates="ingredients"
    )
