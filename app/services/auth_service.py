"""
Authentication service.
"""
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict

from app.models.user import User
from app.utils.validators import validate_email
from app.config import Config

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class AuthService:
    """Handles user authentication and token management."""

    TOKEN_EXPIRY_HOURS = 24

    def __init__(self, config: Config):
        self.config = config
        self._users: Dict[str, User] = {}       # username -> User
        self._tokens: Dict[str, dict] = {}       # token -> {username, expires_at}

    def register(self, username: str, email: str, password: str, **kwargs) -> User:
        """Register a new user."""
        if username in self._users:
            raise ValueError(f"Username '{username}' is already taken.")
        if not validate_email(email):
            raise ValueError(f"Invalid email: {email}")
        user = User.create(username=username, email=email, password=password, **kwargs)
        self._users[username] = user
        logger.info(f"Registered new user: {username}")
        return user

    def login(self, username: str, password: str) -> str:
        """Authenticate and return a session token."""
        user = self._users.get(username)
        if not user or not user.check_password(password):
            raise AuthenticationError("Invalid username or password.")
        if not user.is_active:
            raise AuthenticationError("Account is deactivated.")
        token = self._generate_token()
        self._tokens[token] = {
            "username": username,
            "expires_at": datetime.utcnow() + timedelta(hours=self.TOKEN_EXPIRY_HOURS),
        }
        user.last_login = datetime.utcnow()
        logger.info(f"User '{username}' logged in.")
        return token

    def logout(self, token: str) -> None:
        """Invalidate a session token."""
        if token in self._tokens:
            username = self._tokens.pop(token)["username"]
            logger.info(f"User '{username}' logged out.")

    def get_user_from_token(self, token: str) -> Optional[User]:
        """Retrieve the user associated with a valid token."""
        token_data = self._tokens.get(token)
        if not token_data:
            return None
        if datetime.utcnow() > token_data["expires_at"]:
            self._tokens.pop(token)
            return None
        return self._users.get(token_data["username"])

    def _generate_token(self) -> str:
        return secrets.token_urlsafe(32)
