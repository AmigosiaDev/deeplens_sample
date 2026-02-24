"""
Application entry point — wires together config, services, and a demo workflow.
"""
import logging
import sys

from app.config import Config
from app.models.user import User
from app.models.product import Product, ProductCategory, ProductVariant
from app.services.auth_service import AuthService, AuthenticationError
from app.services.email_service import EmailService
from app.services.payment_service import PaymentService
from app.utils.helpers import format_currency, paginate
from data.loader import DataLoader
from data.processor import DataProcessor


def setup_logging(config: Config) -> None:
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL, logging.INFO),
        format=config.LOG_FORMAT,
    )


def demo_user_flow(auth: AuthService, email: EmailService) -> User:
    """Register a user, log them in, and send a welcome email."""
    logger = logging.getLogger(__name__)

    logger.info("=== User Registration Flow ===")
    user = auth.register(
        username="john_doe",
        email="john@example.com",
        password="SecurePass1",
        first_name="John",
        last_name="Doe",
    )

    token = auth.login("john_doe", "SecurePass1")
    logger.info(f"Login token: {token[:10]}...")

    email.send_welcome_email(user.email, user.username, user.full_name)
    logger.info(f"Welcome email sent to {user.email}")

    return user



def demo_product_catalog() -> list:
    """Build a small product catalog."""
    logger = logging.getLogger(__name__)
    logger.info("=== Building Product Catalog ===")

    products = [
        Product("Gaming Laptop", 1299.99, ProductCategory.ELECTRONICS,
                description="High-performance gaming laptop"),
        Product("Python Cookbook", 39.99, ProductCategory.BOOKS,
                description="Advanced Python recipes"),
        Product("Running Shoes", 89.99, ProductCategory.CLOTHING),
        Product("Organic Coffee", 14.99, ProductCategory.FOOD),
    ]

    # Add variants to the shoes
    products[2].add_variant(ProductVariant("SHOE-BLK-42", color="Black", size="42", stock=10))
    products[2].add_variant(ProductVariant("SHOE-WHT-43", color="White", size="43", stock=5))

    for p in products:
        logger.info(f"  {p.name} - {p.formatted_price} | stock: {p.total_stock}")

    page_items, total_pages = paginate(products, page=1, page_size=3)
    logger.info(f"Page 1 of {total_pages}: {[p.name for p in page_items]}")

    return products


def demo_payment_flow(payment: PaymentService, email: EmailService, user: User) -> None:
    """Process a sample payment and send confirmation."""
    logger = logging.getLogger(__name__)
    logger.info("=== Payment Flow ===")

    VALID_TEST_CARD = "4532015112830366"
    tx = payment.charge(149.99, VALID_TEST_CARD)
    logger.info(f"Charged: {tx['formatted_amount']} | Status: {tx['status']}")

    email.send_order_confirmation(
        user.email, user.full_name, tx["transaction_id"][:8], tx["amount"]
    )

    refund = payment.refund(tx["transaction_id"])
    logger.info(f"Refund status: {refund['status']}")


def demo_data_pipeline(config: Config) -> None:
    """Run a sample data processing pipeline."""
    logger = logging.getLogger(__name__)
    logger.info("=== Data Pipeline ===")

    raw_data = [
        {"name": "  alice ", "category": "FOOD", "price": "12.5"},
        {"name": "bob", "category": "ELECTRONICS", "price": "499"},
        {"name": "", "category": "BOOKS", "price": "9.99"},         # will be dropped
        {"name": "carol", "category": "clothing", "price": "bad"},  # will be dropped
    ]

    processor = DataProcessor()
    result = (
        processor
        .add_step(lambda r: DataProcessor.drop_missing(r, ["name", "price"]))
        .add_step(lambda r: DataProcessor.normalize_strings(r, ["name", "category"]))
        .add_step(lambda r: DataProcessor.cast_numeric(r, ["price"]))
        .run(raw_data)
    )

    stats = DataProcessor.compute_stats(result, "price")
    logger.info(f"Processed {len(result)} records. Stats: {stats}")
    grouped = DataProcessor.group_by(result, "category")
    for category, items in grouped.items():
        logger.info(f"  [{category}] {len(items)} item(s)")


def main() -> None:
    config = Config()
    config.DEBUG = True
    setup_logging(config)

    auth = AuthService(config)
    email = EmailService(config)
    payment = PaymentService(config)

    user = demo_user_flow(auth, email)
    demo_product_catalog()
    demo_payment_flow(payment, email, user)
    demo_data_pipeline(config)

    logging.getLogger(__name__).info("All demo flows completed successfully.")


if __name__ == "__main__":
    main()
