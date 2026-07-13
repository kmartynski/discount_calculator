import pytest

from discount_calculator import (
    CartItem,
    FixedDiscount,
    Money,
    PercentageDiscount,
    VolumeDiscount,
)


@pytest.fixture
def make_item():
    def _factory(code: str, amount: int, qty: int, currency: str = "EUR") -> CartItem:
        return CartItem(code=code, price=Money(amount, currency), quantity=qty)

    return _factory


@pytest.fixture
def fixed_100_eur():
    return FixedDiscount(100, "EUR")


@pytest.fixture
def pct_10():
    return PercentageDiscount(10)


@pytest.fixture
def volume_100_eur_min10():
    return VolumeDiscount(100, "EUR", min_quantity=10)
