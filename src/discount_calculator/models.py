from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str


@dataclass(frozen=True)
class CartItem:
    code: str
    price: Money
    quantity: int
