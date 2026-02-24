"""
Tests for User and Product models.
"""
import pytest
from datetime import datetime

from app.models.user import User, Address
from app.models.product import Product, ProductVariant, ProductCategory
from app.utils.validators import validate_email, validate_password, validate_card_number


# ------------------------------------------------------------------ #
# User tests
# ------------------------------------------------------------------ #

class TestUserModel:

    def test_create_user(self):
        user = User.create("alice", "alice@example.com", "Password1")
        assert user.username == "alice"
        assert user.email == "alice@example.com"
        assert user.is_active is True
        assert user.is_admin is False

    def test_password_hashing(self):
        user = User.create("bob", "bob@example.com", "Password1")
        assert user.check_password("Password1") is True
        assert user.check_password("wrongpassword") is False

    def test_invalid_email_raises(self):
        with pytest.raises(ValueError):
            User("charlie", "not-an-email")

    def test_invalid_password_raises(self):
        user = User("dave", "dave@example.com")
        with pytest.raises(ValueError):
            user.set_password("short")

    def test_full_name(self):
        user = User("eve", "eve@example.com", first_name="Eve", last_name="Smith")
        assert user.full_name == "Eve Smith"

    def test_add_address(self):
        user = User.create("frank", "frank@example.com", "Password1")
        addr = Address("123 Main St", "Springfield", "IL", "62701")
        user.add_address(addr)
        assert len(user.addresses) == 1
        assert "123 Main St" in str(user.addresses[0])

    def test_to_dict(self):
        user = User.create("gina", "gina@example.com", "Password1")
        d = user.to_dict()
        assert d["username"] == "gina"
        assert "email" in d


# ------------------------------------------------------------------ #
# Product tests
# ------------------------------------------------------------------ #

class TestProductModel:

    def test_create_product(self):
        p = Product("Laptop", 999.99, ProductCategory.ELECTRONICS)
        assert p.name == "Laptop"
        assert p.base_price == 999.99
        assert p.product_id is not None

    def test_formatted_price(self):
        p = Product("Book", 14.99, ProductCategory.BOOKS)
        assert p.formatted_price == "$14.99"

    def test_apply_discount(self):
        p = Product("Shirt", 50.0, ProductCategory.CLOTHING)
        assert p.apply_discount(20) == 40.0

    def test_invalid_discount_raises(self):
        p = Product("Shirt", 50.0, ProductCategory.CLOTHING)
        with pytest.raises(ValueError):
            p.apply_discount(110)

    def test_total_stock_no_variants(self):
        p = Product("Apple", 1.5, ProductCategory.FOOD)
        assert p.total_stock == -1  # unlimited

    def test_total_stock_with_variants(self):
        p = Product("T-Shirt", 25.0, ProductCategory.CLOTHING)
        p.add_variant(ProductVariant("TS-RED-M", color="Red", size="M", stock=10))
        p.add_variant(ProductVariant("TS-BLU-L", color="Blue", size="L", stock=5))
        assert p.total_stock == 15

    def test_get_variant_by_sku(self):
        p = Product("Shoes", 80.0, ProductCategory.CLOTHING)
        v = ProductVariant("SH-BLK-42", color="Black", size="42", stock=3)
        p.add_variant(v)
        assert p.get_variant_by_sku("SH-BLK-42") is v
        assert p.get_variant_by_sku("MISSING") is None


# ------------------------------------------------------------------ #
# Validator tests
# ------------------------------------------------------------------ #

class TestValidators:

    def test_valid_emails(self):
        assert validate_email("user@example.com") is True
        assert validate_email("user.name+tag@domain.co.uk") is True

    def test_invalid_emails(self):
        assert validate_email("not-an-email") is False
        assert validate_email("") is False
        assert validate_email("@domain.com") is False

    def test_valid_passwords(self):
        assert validate_password("Secure1Pass") is True

    def test_invalid_passwords(self):
        assert validate_password("short1A") is False       # too short
        assert validate_password("alllowercase1") is False  # no uppercase
        assert validate_password("ALLUPPERCASE1") is False  # no lowercase
        assert validate_password("NoDigitsHere") is False   # no digit

    def test_luhn_valid_card(self):
        assert validate_card_number("4532015112830366") is True   # Visa test
        assert validate_card_number("5425233430109903") is True   # Mastercard test

    def test_luhn_invalid_card(self):
        assert validate_card_number("1234567890123456") is False
        assert validate_card_number("0000") is False
