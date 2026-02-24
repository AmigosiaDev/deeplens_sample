"""
Product model definition.
"""
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum

from app.utils.helpers import format_currency, generate_sku


class ProductCategory(Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    FOOD = "food"
    BOOKS = "books"
    OTHER = "other"


@dataclass
class ProductVariant:
    """Represents a size/color variant of a product."""
    sku: str
    color: Optional[str] = None
    size: Optional[str] = None
    stock: int = 0
    price_modifier: float = 0.0


@dataclass
class Product:
    """Represents a store product."""
    name: str
    base_price: float
    category: ProductCategory
    description: str = ""
    product_id: Optional[str] = None
    variants: List[ProductVariant] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_available: bool = True

    def __post_init__(self):
        if self.product_id is None:
            self.product_id = generate_sku(self.name, self.category.value)

    @property
    def formatted_price(self) -> str:
        return format_currency(self.base_price)

    @property
    def total_stock(self) -> int:
        """Sum of stock across all variants, or -1 if no variants (unlimited)."""
        if not self.variants:
            return -1  # unlimited
        return sum(v.stock for v in self.variants)

    def add_variant(self, variant: ProductVariant) -> None:
        self.variants.append(variant)

    def get_variant_by_sku(self, sku: str) -> Optional[ProductVariant]:
        for variant in self.variants:
            if variant.sku == sku:
                return variant
        return None

    def apply_discount(self, percent: float) -> float:
        """Return discounted price (does not mutate the object)."""
        if not (0 < percent < 100):
            raise ValueError("Discount percent must be between 0 and 100.")
        return round(self.base_price * (1 - percent / 100), 2)

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.base_price,
            "formatted_price": self.formatted_price,
            "category": self.category.value,
            "total_stock": self.total_stock,
            "is_available": self.is_available,
        }
