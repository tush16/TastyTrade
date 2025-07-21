import httpx
import asyncio


class EquitiesService:
    def __init__(self, session_token: str):
        self.session_token = session_token
        self.base_url = "https://api.cert.tastyworks.com"

    async def _fetch_equity(self, client: httpx.AsyncClient, symbol: str):
        headers = {
            "Authorization": self.session_token,
            "Accept": "application/json",
        }
        url = f"{self.base_url}/instruments/equities/{symbol}"
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get("data", {})
            if data:
                return {
                    "symbol": data.get("symbol"),
                    "description": data.get("description"),
                    "listed_market": data.get("listed-market"),
                    "instrument_type": data.get("instrument-type"),
                    "active": data.get("active"),
                    "is_etf": data.get("is-etf"),
                    "lendability": data.get("lendability"),
                    "is_illiquid": data.get("is-illiquid"),
                    "is_closing_only": data.get("is-closing-only"),
                    "tick_sizes": data.get("tick-sizes"),
                }
        return None

    async def list_equities(self):
        symbols = [
            "AAPL",
            "MSFT",
            "GOOG",
            "TSLA",
            "AMZN",
            "META",
            "NFLX",
            "NVDA",
            "INTC",
            "AMD",
        ]
        async with httpx.AsyncClient() as client:
            tasks = [self._fetch_equity(client, symbol) for symbol in symbols]
            results = await asyncio.gather(*tasks)
        return [stock for stock in results if stock is not None]

    async def get_active_equities(
        self,
        page_offset: int = 0,
        per_page: int = 500,
        lendability: str = "Easy To Borrow",
    ):
        url = f"{self.base_url}/instruments/equities/active"
        headers = {"Authorization": self.session_token, "Accept": "application/json"}
        params = {
            "page-offset": str(page_offset),
            "per-page": str(per_page),
        }

        if lendability in ["Easy To Borrow", "Locate Required", "Preborrow"]:
            params["lendability"] = lendability

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get("data", {})
            else:
                raise Exception(
                    f"Upstream error {response.status_code}: {response.text}"
                )

    async def search_equities(self, query: str):
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": self.session_token,
                "Accept": "application/json",
            }
            url = f"{self.base_url}/symbols/search/{query}"
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json().get("data", {})
                items = data.get("items", [])
                return [
                    {
                        "symbol": item.get("symbol"),
                        "description": item.get("description"),
                    }
                    for item in items
                ]
            return []
