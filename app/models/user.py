"""
User model definition.
"""
import hashlib
import secrets
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field

from app.utils.validators import validate_email, validate_password


@dataclass
class Address:
    """Represents a physical address."""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"

    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}, {self.country}"


@dataclass
class User:
    """Represents an application user."""
    username: str
    email: str
    _password_hash: str = field(default="", repr=False)
    first_name: str = ""
    last_name: str = ""
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    addresses: List[Address] = field(default_factory=list)

    def __post_init__(self):
        if not validate_email(self.email):
            raise ValueError(f"Invalid email address: {self.email}")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def set_password(self, raw_password: str) -> None:
        """Hash and store a password."""
        if not validate_password(raw_password):
            raise ValueError("Password does not meet requirements.")
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256(f"{salt}{raw_password}".encode()).hexdigest()
        self._password_hash = f"{salt}:{hashed}"

    def check_password(self, raw_password: str) -> bool:
        """Verify a raw password against the stored hash."""
        if not self._password_hash:
            return False
        salt, hashed = self._password_hash.split(":", 1)
        return hashlib.sha256(f"{salt}{raw_password}".encode()).hexdigest() == hashed

    def add_address(self, address: Address) -> None:
        self.addresses.append(address)

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def create(cls, username: str, email: str, password: str, **kwargs) -> "User":
        """Factory method to create a new user with a hashed password."""
        user = cls(username=username, email=email, **kwargs)
        user.set_password(password)
        return user
