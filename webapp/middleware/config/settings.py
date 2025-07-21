import os
from dotenv import load_dotenv


class Settings:
    """Centralized configuration with env + Key Vault support."""

    def __init__(self):
        load_dotenv()

        # ─── Environment ────────────────────────────────────────────────
        self.ENV: str = os.getenv("ENV")
        self.BASE_URL: str = os.getenv("BASE_URL")


# Singleton instance to be used throughout the app
settings = Settings()
