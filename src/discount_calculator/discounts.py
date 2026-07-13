from abc import ABC, abstractmethod

from .models import CartItem


class Discount(ABC):
    def __init__(self, product_codes: list[str] | None = None):
        # None = applies to all products; frozenset for O(1) lookup and immutability
        self.product_codes: frozenset[str] | None = (
            frozenset(product_codes) if product_codes is not None else None
        )

    def applies_to(self, item: CartItem) -> bool:
        return self.product_codes is None or item.code in self.product_codes

    @abstractmethod
    def discount_amount(self, item: CartItem) -> int:
        """Return the discount in the same units as CartItem.price.amount."""
        ...


class FixedDiscount(Discount):
    def __init__(self, amount: int, currency: str, product_codes: list[str] | None = None):
        super().__init__(product_codes)
        self.amount = amount
        self.currency = currency

    def discount_amount(self, item: CartItem) -> int:
        if item.price.currency != self.currency:
            return 0
        return self.amount  # flat per-line: the same amount regardless of quantity


class PercentageDiscount(Discount):
    def __init__(self, percentage: int, product_codes: list[str] | None = None):
        super().__init__(product_codes)
        self.percentage = percentage

    def discount_amount(self, item: CartItem) -> int:
        line_total = item.price.amount * item.quantity
        # floor division: currency amounts are always whole units
        return line_total * self.percentage // 100


class VolumeDiscount(Discount):
    def __init__(
        self,
        amount: int,
        currency: str,
        min_quantity: int,
        product_codes: list[str] | None = None,
    ):
        super().__init__(product_codes)
        self.amount = amount
        self.currency = currency
        self.min_quantity = min_quantity

    def discount_amount(self, item: CartItem) -> int:
        if item.price.currency != self.currency:
            return 0
        if item.quantity >= self.min_quantity:
            return self.amount
        return 0
