import httpx
from config.logging import logger
from config.settings import settings


class AuthService:
    @staticmethod
    def login(login: str, password: str):
        try:
            base_url = settings.BASE_URL
            logger.info(base_url)
            url = f"{base_url}/sessions"

            payload = {"login": login, "password": password}

            headers = {"Content-Type": "application/json", "Accept": "application/json"}

            response = httpx.post(url, json=payload, headers=headers)

            if response.status_code == 201:
                session_token = response.json()["data"]["session-token"]
                logger.info("Login success: session token retrieved")
                return session_token
            else:
                logger.error(f"Login failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Login failed due to error: {e}")
            return None
