from .discounts import Discount
from .models import CartItem, Money


class DiscountCalculator:
    def __init__(self, discounts: list[Discount]):
        self.discounts = discounts

    def calculate(self, items: list[CartItem]) -> Money:
        if not items:
            raise ValueError("Cannot calculate total for an empty cart")

        currency = items[0].price.currency
        if any(item.price.currency != currency for item in items[1:]):
            raise ValueError("All cart items must share the same currency")

        total = 0

        for item in items:
            line_total = item.price.amount * item.quantity

            applicable = [discount for discount in self.discounts if discount.applies_to(item)]
            best_discount = max(
                (discount.discount_amount(item) for discount in applicable),
                default=0,
            )

            discounted = max(0, line_total - best_discount)
            total += discounted

        return Money(total, currency)
