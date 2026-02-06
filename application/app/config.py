"""
Application configuration using dataclasses.
Configuration is loaded from environment variables with sensible defaults
for development. In production, set SECRET_KEY and DATABASE_URL to secure values.
"""
import os
from dataclasses import dataclass

@dataclass
class Config:
    """Base configuration."""
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key")
    DEBUG: bool = False
    TESTING: bool = False
    # Database configuration
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "sqlite:///news_flash.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

@dataclass
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG: bool = True

@dataclass
class TestingConfig(Config):
    """Testing configuration."""
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"

@dataclass
class ProductionConfig(Config):
    """Production configuration."""
    pass

config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}