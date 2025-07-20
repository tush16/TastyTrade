import os
from dotenv import load_dotenv
from typing import Dict


class Settings:
    """Centralized configuration with env + Key Vault support."""

    def __init__(self):
        # Load .env and Key Vault secrets
        load_dotenv()

        # ─── Environment ────────────────────────────────────────────────
        self.ENV: str = os.getenv("ENV", "LOCAL")


# Singleton instance to be used throughout the app
settings = Settings()
