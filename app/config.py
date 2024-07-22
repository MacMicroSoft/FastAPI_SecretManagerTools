import os
from pydantic_settings import BaseSettings
from pathlib import Path
import pytest


class Settings(BaseSettings):
    POSTGRESQL_HOST: str
    POSTGRESQL_PORT: int
    POSTGRESQL_NAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_USER: str

    SECRET_KEY: str
    TEST_POSTGRESQL: str
    JWT_REFRESH_SECRET_KEY: str
    ALGORITHM: str
    TIMEOUT: int
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    adminapikey: str

    SERVER: str

    class Config:
        env_file = Path(__file__).resolve().parent / ".env"
        env_file_encoding = 'utf-8'


setting = Settings()

