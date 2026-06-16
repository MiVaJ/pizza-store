from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

# Тип данных для конвертации копеек в рубли
RublesInt = Annotated[int, PlainSerializer(lambda x: x // 100, return_type=int)]


class IngredientResponse(BaseModel):
    """Схема для отправки соусов и ингредиентов."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Уникальный ID соуса или ингредиента")
    name: str = Field(..., description="Название соуса/ингредиента")
    price: RublesInt = Field(..., description="Стоимость в рублях")
    image_url: str | None = Field(
        None, description="Ссылка на картинку соуса/ингредиента"
    )
    is_sauce: bool = Field(
        ..., description="Флаг: True — соус для корзины, False — топпинг для пиццы"
    )


class PizzaResponse(BaseModel):
    """Схема для отправки информации о пицце на фронтенд."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Уникальный ID пиццы")
    name: str = Field(..., description="Название пиццы")
    description: str = Field(..., description="Описание состава и ингредиентов")
    price: RublesInt = Field(..., description="Стоимость в рублях")
    image_url: str | None = Field(None, description="Ссылка на красивую картинку пиццы")
    is_available: bool = Field(..., description="Есть ли пицца в наличии в ресторане")

    ingredients: list[IngredientResponse] = Field(
        default=[],
        description=(
            "Список всех доступных для этой пиццы соусов и дополнительных ингредиентов"
        ),
    )
