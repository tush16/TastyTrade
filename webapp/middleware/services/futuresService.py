import httpx


class FuturesService:
    def __init__(self, session_token: str):
        self.session_token = session_token
        self.base_url = "https://api.cert.tastyworks.com"

    def _headers(self):
        return {
            "Authorization": self.session_token,
            "Accept": "application/json",
        }

    async def list_futures(self):
        url = f"{self.base_url}/instruments/futures"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers(), timeout=10)
            data = resp.json().get("data", {}).get("items", [])
        return data

    async def get_future(self, symbol: str):
        url = f"{self.base_url}/instruments/futures/{symbol}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers(), timeout=10)
            return resp.json().get("data", {})
