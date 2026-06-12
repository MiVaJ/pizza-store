import pytest

from src.models.order import OrderStatus
from src.schemas.order import OrderStatusUpdate


def test_valid_transition_pending_to_cooking():
    update = OrderStatusUpdate(status=OrderStatus.COOKING)
    update.validate_transition(current_status=OrderStatus.PENDING)  # не бросает


def test_valid_transition_cooking_to_delivering():
    update = OrderStatusUpdate(status=OrderStatus.DELIVERING)
    update.validate_transition(current_status=OrderStatus.COOKING)


def test_valid_transition_delivering_to_completed():
    update = OrderStatusUpdate(status=OrderStatus.COMPLETED)
    update.validate_transition(current_status=OrderStatus.DELIVERING)


def test_valid_cancellation_from_pending():
    update = OrderStatusUpdate(status=OrderStatus.CANCELLED)
    update.validate_transition(current_status=OrderStatus.PENDING)


def test_same_status_is_valid():
    """Передать тот же статус — валидно."""
    update = OrderStatusUpdate(status=OrderStatus.PENDING)
    update.validate_transition(current_status=OrderStatus.PENDING)


@pytest.mark.parametrize(
    "current,new",
    [
        (OrderStatus.COMPLETED, OrderStatus.PENDING),
        (OrderStatus.COMPLETED, OrderStatus.COOKING),
        (OrderStatus.CANCELLED, OrderStatus.COOKING),
        (OrderStatus.PENDING, OrderStatus.COMPLETED),
        (OrderStatus.COOKING, OrderStatus.PENDING),
        (OrderStatus.DELIVERING, OrderStatus.PENDING),
    ],
)
def test_invalid_transitions(current, new):
    """Недопустимые переходы бросают ValueError."""
    update = OrderStatusUpdate(status=new)
    with pytest.raises(ValueError, match="Невозможно перевести"):
        update.validate_transition(current_status=current)
