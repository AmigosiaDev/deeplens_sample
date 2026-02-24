"""
General helper utilities.
"""
import uuid
import math
import hashlib
import logging
from typing import TypeVar, List, Tuple, Any

logger = logging.getLogger(__name__)

T = TypeVar("T")


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format a float as a currency string."""
    symbols = {"USD": "$", "EUR": "€", "GBP": "£", "INR": "₹"}
    symbol = symbols.get(currency.upper(), currency)
    return f"{symbol}{amount:,.2f}"


def generate_sku(name: str, category: str) -> str:
    """Generate a short unique SKU based on product name and category."""
    seed = f"{name.upper()}-{category.upper()}"
    digest = hashlib.md5(seed.encode()).hexdigest()[:6].upper()
    return f"{category[:3].upper()}-{digest}"


def paginate(items: List[T], page: int, page_size: int) -> Tuple[List[T], int]:
    """
    Paginate a list.
    Returns (page_items, total_pages).
    """
    if page_size <= 0:
        raise ValueError("page_size must be positive.")
    total_pages = math.ceil(len(items) / page_size) if items else 1
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], total_pages


def chunk_list(items: List[Any], size: int) -> List[List[Any]]:
    """Split a list into chunks of a given size."""
    return [items[i : i + size] for i in range(0, len(items), size)]


def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge two dictionaries; override takes precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def generate_id(prefix: str = "") -> str:
    """Generate a prefixed UUID string."""
    uid = str(uuid.uuid4()).replace("-", "")
    return f"{prefix}{uid}" if prefix else uid
