import pytest

from discount_calculator import (
    DiscountCalculator,
    FixedDiscount,
    Money,
    PercentageDiscount,
    VolumeDiscount,
)


class TestCalculatorWithFixedDiscount:
    def test_applies_to_all_products(self, make_item):
        calc = DiscountCalculator([FixedDiscount(100, "EUR")])
        assert calc.calculate([make_item("SKU1", 500, 1)]) == Money(400, "EUR")

    def test_applies_to_specific_matching_product(self, make_item):
        calc = DiscountCalculator([FixedDiscount(100, "EUR", product_codes=["SKU1"])])
        assert calc.calculate([make_item("SKU1", 500, 1)]) == Money(400, "EUR")

    def test_skips_non_matching_product(self, make_item):
        calc = DiscountCalculator([FixedDiscount(100, "EUR", product_codes=["SKU2"])])
        assert calc.calculate([make_item("SKU1", 500, 1)]) == Money(500, "EUR")

    def test_ignored_on_currency_mismatch(self, make_item):
        calc = DiscountCalculator([FixedDiscount(100, "USD")])
        assert calc.calculate([make_item("SKU1", 500, 1, currency="EUR")]) == Money(500, "EUR")


class TestCalculatorWithPercentageDiscount:
    def test_applies_to_all_products(self, make_item):
        calc = DiscountCalculator([PercentageDiscount(10)])
        # line total = 1000*2 = 2000, 10% off → 1800
        assert calc.calculate([make_item("SKU1", 1000, 2)]) == Money(1800, "EUR")

    def test_applies_only_to_specified_product(self, make_item):
        calc = DiscountCalculator([PercentageDiscount(50, product_codes=["SALE"])])
        result = calc.calculate([make_item("SALE", 1000, 1), make_item("FULL", 1000, 1)])
        assert result == Money(1500, "EUR")


class TestCalculatorWithVolumeDiscount:
    def test_discount_applied_when_threshold_met(self, make_item):
        calc = DiscountCalculator([VolumeDiscount(100, "EUR", min_quantity=10)])
        # line total = 50*10 = 500, discount = 100 → 400
        assert calc.calculate([make_item("SKU1", 50, 10)]) == Money(400, "EUR")

    def test_no_discount_below_threshold(self, make_item):
        calc = DiscountCalculator([VolumeDiscount(100, "EUR", min_quantity=10)])
        assert calc.calculate([make_item("SKU1", 50, 9)]) == Money(450, "EUR")

    def test_discount_applied_at_exact_threshold(self, make_item):
        calc = DiscountCalculator([VolumeDiscount(100, "EUR", min_quantity=5)])
        assert calc.calculate([make_item("SKU1", 50, 5)]) == Money(150, "EUR")


class TestBestDiscountSelection:
    def test_best_discount_wins_per_line(self, make_item):
        discounts = [
            FixedDiscount(50, "EUR"),
            PercentageDiscount(20),  # 20% of 500 = 100 > 50
        ]
        calc = DiscountCalculator(discounts)
        assert calc.calculate([make_item("SKU1", 500, 1)]) == Money(400, "EUR")

    def test_each_line_independently_picks_best_discount(self, make_item):
        discounts = [
            FixedDiscount(50, "EUR", product_codes=["A"]),
            PercentageDiscount(10, product_codes=["B"]),
        ]
        calc = DiscountCalculator(discounts)
        result = calc.calculate(
            [
                make_item("A", 200, 1),  # 200 - 50 = 150
                make_item("B", 1000, 1),  # 1000 - 100 = 900
            ]
        )
        assert result == Money(1050, "EUR")

    def test_volume_beats_fixed_when_larger(self, make_item):
        discounts = [
            FixedDiscount(50, "EUR"),
            VolumeDiscount(200, "EUR", min_quantity=5),
        ]
        calc = DiscountCalculator(discounts)
        # volume discount (200) > fixed (50)
        assert calc.calculate([make_item("SKU1", 100, 5)]) == Money(300, "EUR")


class TestEdgeCases:
    def test_empty_cart_raises(self):
        calc = DiscountCalculator([FixedDiscount(100, "EUR")])
        with pytest.raises(ValueError, match="empty cart"):
            calc.calculate([])

    def test_mixed_currency_cart_raises(self, make_item):
        calc = DiscountCalculator([])
        with pytest.raises(ValueError, match="same currency"):
            calc.calculate(
                [
                    make_item("A", 100, 1, currency="EUR"),
                    make_item("B", 100, 1, currency="USD"),
                ]
            )

    def test_discount_capped_at_line_total_fixed(self, make_item):
        calc = DiscountCalculator([FixedDiscount(1000, "EUR")])
        assert calc.calculate([make_item("SKU1", 50, 1)]) == Money(0, "EUR")

    def test_discount_capped_at_line_total_volume(self, make_item):
        calc = DiscountCalculator([VolumeDiscount(9999, "EUR", min_quantity=1)])
        assert calc.calculate([make_item("SKU1", 50, 2)]) == Money(0, "EUR")

    def test_no_discounts_returns_full_total(self, make_item):
        calc = DiscountCalculator([])
        assert calc.calculate([make_item("SKU1", 300, 3)]) == Money(900, "EUR")

    def test_multiple_items_no_discount(self, make_item):
        calc = DiscountCalculator([])
        result = calc.calculate([make_item("A", 100, 2), make_item("B", 200, 1)])
        assert result == Money(400, "EUR")

    def test_single_item_no_applicable_discount(self, make_item):
        calc = DiscountCalculator([FixedDiscount(100, "EUR", product_codes=["OTHER"])])
        assert calc.calculate([make_item("SKU1", 300, 1)]) == Money(300, "EUR")

    def test_zero_quantity_item_contributes_nothing(self, make_item):
        calc = DiscountCalculator([FixedDiscount(100, "EUR")])
        assert calc.calculate([make_item("SKU1", 500, 0)]) == Money(0, "EUR")

    def test_fixed_discount_is_flat_per_line_regardless_of_quantity(self, make_item):
        calc = DiscountCalculator([FixedDiscount(100, "EUR")])
        # 10 units at 50 EUR = 500 EUR line total; fixed discount is 100 EUR per line, not per unit
        assert calc.calculate([make_item("SKU1", 50, 10)]) == Money(400, "EUR")
