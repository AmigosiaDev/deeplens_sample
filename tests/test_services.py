"""
Tests for services — AuthService, EmailService, PaymentService.
"""
import pytest

from app.config import Config
from app.services.auth_service import AuthService, AuthenticationError
from app.services.email_service import EmailService
from app.services.payment_service import PaymentService


@pytest.fixture
def config():
    cfg = Config()
    cfg.DEBUG = True
    return cfg


@pytest.fixture
def auth(config):
    return AuthService(config)


@pytest.fixture
def email(config):
    return EmailService(config)


@pytest.fixture
def payment(config):
    return PaymentService(config)


# ------------------------------------------------------------------ #
# AuthService tests
# ------------------------------------------------------------------ #

class TestAuthService:

    def test_register_and_login(self, auth):
        auth.register("alice", "alice@example.com", "Password1")
        token = auth.login("alice", "Password1")
        assert token is not None
        assert len(token) > 10

    def test_login_wrong_password(self, auth):
        auth.register("bob", "bob@example.com", "Password1")
        with pytest.raises(AuthenticationError):
            auth.login("bob", "wrongpassword")

    def test_login_unknown_user(self, auth):
        with pytest.raises(AuthenticationError):
            auth.login("nobody", "Password1")

    def test_get_user_from_valid_token(self, auth):
        auth.register("carol", "carol@example.com", "Password1")
        token = auth.login("carol", "Password1")
        user = auth.get_user_from_token(token)
        assert user is not None
        assert user.username == "carol"

    def test_get_user_from_invalid_token(self, auth):
        assert auth.get_user_from_token("fake-token") is None

    def test_logout_invalidates_token(self, auth):
        auth.register("dave", "dave@example.com", "Password1")
        token = auth.login("dave", "Password1")
        auth.logout(token)
        assert auth.get_user_from_token(token) is None

    def test_duplicate_registration_raises(self, auth):
        auth.register("eve", "eve@example.com", "Password1")
        with pytest.raises(ValueError):
            auth.register("eve", "eve2@example.com", "Password1")


# ------------------------------------------------------------------ #
# EmailService tests
# ------------------------------------------------------------------ #

class TestEmailService:

    def test_send_welcome_email(self, email):
        result = email.send_welcome_email("test@example.com", "frank", "Frank")
        assert result is True
        assert email.sent_count == 1

    def test_send_order_confirmation(self, email):
        result = email.send_order_confirmation("test@example.com", "Gina", "ORD-001", 149.99)
        assert result is True
        assert email.sent_count == 1


# ------------------------------------------------------------------ #
# PaymentService tests
# ------------------------------------------------------------------ #

class TestPaymentService:

    VALID_CARD = "4532015112830366"  # Luhn-valid Visa test number

    def test_successful_charge(self, payment):
        tx = payment.charge(50.0, self.VALID_CARD)
        assert tx["status"] == "success"
        assert tx["amount"] == 50.0
        assert "****" in tx["card"]

    def test_charge_invalid_amount(self, payment):
        with pytest.raises(ValueError):
            payment.charge(-10.0, self.VALID_CARD)

    def test_charge_invalid_card(self, payment):
        with pytest.raises(ValueError):
            payment.charge(10.0, "1234567890123456")

    def test_refund_success(self, payment):
        tx = payment.charge(75.0, self.VALID_CARD)
        refunded = payment.refund(tx["transaction_id"])
        assert refunded["status"] == "refunded"

    def test_refund_unknown_transaction(self, payment):
        result = payment.refund("nonexistent-id")
        assert result is None

    def test_get_transaction(self, payment):
        tx = payment.charge(20.0, self.VALID_CARD)
        fetched = payment.get_transaction(tx["transaction_id"])
        assert fetched is not None
        assert fetched["amount"] == 20.0
