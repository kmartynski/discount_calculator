from dataclasses import FrozenInstanceError

import pytest

from discount_calculator import CartItem, Money


class TestMoney:
    def test_equal_amount_and_currency(self):
        assert Money(100, "EUR") == Money(100, "EUR")

    def test_not_equal_different_amount(self):
        assert Money(100, "EUR") != Money(200, "EUR")

    def test_not_equal_different_currency(self):
        assert Money(100, "EUR") != Money(100, "USD")

    def test_eq_with_non_money_returns_not_implemented(self):
        assert Money(100, "EUR").__eq__(42) is NotImplemented
        assert Money(100, "EUR").__eq__("100 EUR") is NotImplemented

    def test_repr(self):
        assert repr(Money(100, "EUR")) == "Money(amount=100, currency='EUR')"

    def test_is_immutable(self):
        money = Money(100, "EUR")
        with pytest.raises(FrozenInstanceError):
            money.amount = 200  # type: ignore[misc]


class TestCartItem:
    def test_attributes_are_accessible(self):
        item = CartItem(code="SKU1", price=Money(200, "EUR"), quantity=3)
        assert item.code == "SKU1"
        assert item.price == Money(200, "EUR")
        assert item.quantity == 3

    def test_zero_quantity_gives_zero_line_total(self):
        item = CartItem(code="SKU1", price=Money(500, "EUR"), quantity=0)
        assert item.price.amount * item.quantity == 0

    def test_is_immutable(self):
        item = CartItem(code="SKU1", price=Money(100, "EUR"), quantity=1)
        with pytest.raises(FrozenInstanceError):
            item.quantity = 5  # type: ignore[misc]
