import os
from dotenv import load_dotenv


class Settings:
    """Centralized configuration with env."""

    def __init__(self):
        load_dotenv()

        self.ENV: str = os.getenv("ENV")
        self.BASE_URL: str = os.getenv("BASE_URL")
        self.LOGIN: str = os.getenv("LOGIN")
        self.PASSWORD: str = os.getenv("PASSWORD")
        self.DB_SERVER: str = os.getenv("DB_SERVER")
        self.DB_NAME: str = os.getenv("DB_NAME")
        self.CLIENT_ID: str = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET: str = os.getenv("CLIENT_SECRET")


# Singleton instance to be used throughout the app
settings = Settings()
