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


# Singleton instance to be used throughout the app
settings = Settings()
