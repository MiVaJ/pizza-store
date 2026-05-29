from pydantic import BaseModel, Field


class PizzaResponse(BaseModel):
    """Схема для отправки информации о пицце на фронтенд."""

    id: int = Field(..., description="Уникальный ID пиццы")
    name: str = Field(..., description="Название пиццы")
    description: str = Field(..., description="Описание состава и ингредиентов")
    price: float = Field(..., description="Стоимость в рублях")
    image_url: str | None = Field(None, description="Ссылка на красивую картинку пиццы")
    is_available: bool = Field(..., description="Есть ли пицца в наличии в ресторане")

    class Config:
        from_attributes = True
