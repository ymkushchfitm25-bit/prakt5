"""Конфігурація Flask-додатка."""

import os


class Config:
    """Базова конфігурація."""

    # Підписує сесію та CSRF-токени. Для розробки допустимий ключ за замовчуванням,
    # але його можна перевизначити змінною оточення SECRET_KEY.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-me")
    DEBUG = False


class DevelopmentConfig(Config):
    """Конфігурація для розробки."""

    DEBUG = True


class ProductionConfig(Config):
    """Конфігурація для production."""

    # Лише зі змінної оточення — без значення за замовчуванням у коді
    SECRET_KEY = os.environ.get("SECRET_KEY")


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
