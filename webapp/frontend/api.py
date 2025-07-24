import requests

API_BASE = "http://localhost:8000"


def list_equities(token):
    url = f"{API_BASE}/equities/top"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    return resp.json() if resp.status_code == 200 else []


def search_equities(token, query):
    url = f"{API_BASE}/equities/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"query": query}
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    return resp.json() if resp.status_code == 200 else []


def get_equity_options(token, stock_symbols, active=True, with_expired=False):
    url = f"{API_BASE}/equity-options"
    headers = {"Authorization": f"Bearer {token}"}
    params = [("stock[]", s) for s in stock_symbols] + [
        ("active", str(active).lower()),
        ("with_expired", str(with_expired).lower()),
    ]
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    return resp.json() if resp.status_code == 200 else []


def get_option_chain_nested(token: str, symbol: str):
    url = f"{API_BASE}/option-chains/{symbol}/nested"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code == 200:
        return resp.json().get("items", [])
    else:
        return {"error": f"API error {resp.status_code}: {resp.text}"}


def list_futures(token: str):
    url = f"{API_BASE}/futures"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    else:
        return {"error": f"API error {resp.status_code}: {resp.text}"}


def get_future_detail(token: str, symbol: str):
    clean_symbol = symbol.lstrip("/")
    url = f"{API_BASE}/futures/{clean_symbol}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    else:
        return {"error": f"API error {resp.status_code}: {resp.text}"}
