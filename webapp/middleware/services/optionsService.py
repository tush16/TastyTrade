import httpx
from typing import List, Dict, Union


class OptionsService:
    def __init__(self, session_token: str):
        self.session_token = session_token
        self.base_url = "https://api.cert.tastyworks.com"

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": self.session_token, "Accept": "application/json"}

    async def get_option_chain(self, symbol: str) -> dict:
        url = f"{self.base_url}/option-chains/{symbol}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers(), timeout=10)
            if resp.status_code == 200:
                return resp.json().get("data", {})
            else:
                return {"error": f"Could not fetch option chain for {symbol}"}

    async def get_equity_options(
        self, symbols: List[str], active: bool = True, with_expired: bool = False
    ) -> Union[List[dict], dict]:
        url = f"{self.base_url}/instruments/equity-options"

        params: Dict[str, Union[str, List[str]]] = {
            "active": str(active).lower(),
            "with-expired": str(with_expired).lower(),
            "symbol[]": symbols,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url, headers=self._headers(), params=params, timeout=10
            )
            if resp.status_code == 200:
                return resp.json().get("data", {}).get("items", [])
            else:
                return {"error": f"Upstream error {resp.status_code}: {resp.text}"}
