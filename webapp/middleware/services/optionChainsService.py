import httpx


class OptionChainsService:
    def __init__(self, session_token: str):
        self.session_token = session_token
        self.base_url = "https://api.cert.tastyworks.com"

    def _headers(self):
        return {
            "Authorization": self.session_token,
            "Accept": "application/json",
        }

    async def get_option_chain(self, symbol: str):
        url = f"{self.base_url}/option-chains/{symbol}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers(), timeout=15)
            return resp.json().get("data", {})
