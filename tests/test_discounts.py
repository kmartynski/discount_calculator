from discount_calculator import (
    FixedDiscount,
    PercentageDiscount,
    VolumeDiscount,
)


class TestFixedDiscount:
    def test_applies_to_all_products_when_no_codes(self, make_item):
        discount = FixedDiscount(100, "EUR")
        assert discount.applies_to(make_item("ANY", 500, 1)) is True

    def test_applies_to_matching_product_code(self, make_item):
        discount = FixedDiscount(100, "EUR", product_codes=["SKU1"])
        assert discount.applies_to(make_item("SKU1", 500, 1)) is True

    def test_does_not_apply_to_non_matching_product_code(self, make_item):
        discount = FixedDiscount(100, "EUR", product_codes=["SKU2"])
        assert discount.applies_to(make_item("SKU1", 500, 1)) is False

    def test_discount_amount_correct_currency(self, make_item):
        discount = FixedDiscount(100, "EUR")
        assert discount.discount_amount(make_item("SKU1", 500, 1)) == 100

    def test_discount_amount_zero_on_currency_mismatch(self, make_item):
        discount = FixedDiscount(100, "USD")
        assert discount.discount_amount(make_item("SKU1", 500, 1, currency="EUR")) == 0

    def test_discount_amount_is_flat_regardless_of_quantity(self, make_item):
        discount = FixedDiscount(50, "EUR")
        assert discount.discount_amount(make_item("SKU1", 100, 5)) == 50


class TestPercentageDiscount:
    def test_applies_to_all_products_when_no_codes(self, make_item):
        discount = PercentageDiscount(10)
        assert discount.applies_to(make_item("ANY", 500, 1)) is True

    def test_applies_only_to_specified_product_codes(self, make_item):
        discount = PercentageDiscount(10, product_codes=["SALE"])
        assert discount.applies_to(make_item("SALE", 500, 1)) is True
        assert discount.applies_to(make_item("FULL", 500, 1)) is False

    def test_discount_amount_on_line_total(self, make_item):
        discount = PercentageDiscount(10)
        # price=1000, qty=2 → line_total=2000 → 10% = 200
        assert discount.discount_amount(make_item("SKU1", 1000, 2)) == 200

    def test_discount_amount_single_unit(self, make_item):
        discount = PercentageDiscount(20)
        assert discount.discount_amount(make_item("SKU1", 500, 1)) == 100

    def test_discount_amount_floors_fractional_result(self, make_item):
        discount = PercentageDiscount(10)
        # 10% of 105 = 10.5 → floors to 10
        assert discount.discount_amount(make_item("SKU1", 105, 1)) == 10


class TestVolumeDiscount:
    def test_applies_when_quantity_meets_threshold(self, make_item):
        discount = VolumeDiscount(100, "EUR", min_quantity=10)
        assert discount.discount_amount(make_item("SKU1", 50, 10)) == 100

    def test_applies_when_quantity_exceeds_threshold(self, make_item):
        discount = VolumeDiscount(100, "EUR", min_quantity=10)
        assert discount.discount_amount(make_item("SKU1", 50, 15)) == 100

    def test_no_discount_below_threshold(self, make_item):
        discount = VolumeDiscount(100, "EUR", min_quantity=10)
        assert discount.discount_amount(make_item("SKU1", 50, 9)) == 0

    def test_exact_threshold_is_inclusive(self, make_item):
        discount = VolumeDiscount(100, "EUR", min_quantity=5)
        assert discount.discount_amount(make_item("SKU1", 50, 5)) == 100

    def test_zero_discount_on_currency_mismatch(self, make_item):
        discount = VolumeDiscount(100, "USD", min_quantity=5)
        assert discount.discount_amount(make_item("SKU1", 50, 10, currency="EUR")) == 0

    def test_applies_to_specific_product_codes(self, make_item):
        discount = VolumeDiscount(100, "EUR", min_quantity=5, product_codes=["BULK"])
        assert discount.applies_to(make_item("BULK", 50, 5)) is True
        assert discount.applies_to(make_item("OTHER", 50, 5)) is False
