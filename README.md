# Discount Calculator

An e-commerce discount calculator that applies configurable discount rules to cart items and returns the total value after discounts.

---

## Requirements

- [pyenv](https://github.com/pyenv/pyenv) with Python 3.12 installed
- [uv](https://docs.astral.sh/uv/) for dependency management

---

## Installation

```bash
pyenv local 3.12
uv sync
```

---

## Usage

```python
from discount_calculator import (
    CartItem,
    DiscountCalculator,
    FixedDiscount,
    Money,
    PercentageDiscount,
    VolumeDiscount,
)

# Define available discounts
discounts = [
    FixedDiscount(100, "EUR"),                          # -100 EUR on every item
    PercentageDiscount(10, product_codes=["SALE"]),     # -10% on SALE items only
    VolumeDiscount(200, "EUR", min_quantity=10),        # -200 EUR if qty >= 10
]

# Build cart
cart = [
    CartItem(code="SALE", price=Money(1000, "EUR"), quantity=2),
    CartItem(code="SKU1", price=Money(500, "EUR"), quantity=10),
]

# Calculate total (best discount wins per line)
calculator = DiscountCalculator(discounts)
total = calculator.calculate(cart)
print(total)  # Money(1500, 'EUR')
```

---

## Discount Types

| Type | Rule | Example |
|---|---|---|
| **Fixed** | Deducts a fixed amount from the line | `-100 EUR` |
| **Percentage** | Deducts a percentage of the line total | `-10%` |
| **Volume** | Deducts a fixed amount when quantity meets a threshold | `-100 EUR if at least 10 items` |

All discount types can be scoped to specific product codes via `product_codes=["SKU1", "SKU2"]`, or left as `None` to apply to all products.

**Only one discount applies per cart line** — the one that produces the greatest saving is chosen.

---

## Code Architecture

```
src/discount_calculator/
├── __init__.py      Re-exports the full public API
├── models.py        Money and CartItem data classes
├── discounts.py     Discount ABC and three concrete discount types
└── calculator.py    DiscountCalculator — orchestrates discount selection
```

### `models.py`

- **`Money(amount: int, currency: str)`** — represents a monetary value. `amount` is in the smallest currency unit (e.g. cents).
- **`CartItem(code: str, price: Money, quantity: int)`** — represents one line in a shopping cart.

### `discounts.py`

- **`Discount`** — abstract base class. Subclasses implement:
  - `applies_to(item) -> bool` — checks product code scope.
  - `discount_amount(item) -> int` — returns the saving in the same unit as `price.amount`.
- **`FixedDiscount(amount, currency)`** — flat deduction per line, currency-matched.
- **`PercentageDiscount(percentage)`** — percentage of the line total (`price × quantity`).
- **`VolumeDiscount(amount, currency, min_quantity)`** — flat deduction when `quantity >= min_quantity`, currency-matched.

### `calculator.py`

- **`DiscountCalculator(discounts: list[Discount])`** — accepts a list of discount rules.
- **`calculate(items: list[CartItem]) -> Money`** — for each cart line, collects all applicable discounts, picks the one with the highest `discount_amount`, caps it at the line total, then sums up all discounted line values.

---

## Tests

```
tests/
├── conftest.py          Shared fixtures: make_item factory, common discount instances
├── test_discounts.py    Unit tests for each discount type in isolation
└── test_calculator.py   Integration tests for DiscountCalculator
```

### Running tests

```bash
make test
```

Or directly:

```bash
uv run pytest
```

### Test coverage summary

| Module | What's tested |
|---|---|
| `test_discounts.py` | `applies_to` logic, `discount_amount` calculation, currency mismatch, threshold boundary |
| `test_calculator.py` | Fixed/percentage/volume discounts via `calculate()`, best-discount selection per line, edge cases (empty cart, capped discount, no discounts) |

### Fixtures (`conftest.py`)

| Fixture | Description |
|---|---|
| `make_item(code, amount, qty, currency="EUR")` | Factory function that builds a `CartItem` |
| `fixed_100_eur` | `FixedDiscount(100, "EUR")` |
| `pct_10` | `PercentageDiscount(10)` |
| `volume_100_eur_min10` | `VolumeDiscount(100, "EUR", min_quantity=10)` |

---

## Makefile Commands

| Command | Description |
|---|---|
| `make install` | Install all dependencies with `uv sync` |
| `make lint` | Run `ruff check` on `src` and `tests` |
| `make format` | Run `ruff format` on `src` and `tests` |
| `make test` | Run the full test suite with `pytest` |
| `make check` | Run lint and tests together |
