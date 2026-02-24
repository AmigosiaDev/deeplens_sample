"""
Application configuration settings.
"""
import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Base configuration class."""

    APP_NAME = "SampleApp"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-in-production")

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///sample.db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

    PAYMENT_API_KEY = os.getenv("PAYMENT_API_KEY", "")
    PAYMENT_GATEWAY_URL = os.getenv("PAYMENT_GATEWAY_URL", "https://api.payment.example.com")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def from_json(cls, filepath: str) -> "Config":
        """Load config overrides from a JSON file."""
        config = cls()
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            for key, value in data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {filepath}")
        return config

    def to_dict(self) -> dict:
        """Export config as dictionary (excludes secrets)."""
        return {
            "APP_NAME": self.APP_NAME,
            "DEBUG": self.DEBUG,
            "DATABASE_URL": self.DATABASE_URL,
            "LOG_LEVEL": self.LOG_LEVEL,
        }
