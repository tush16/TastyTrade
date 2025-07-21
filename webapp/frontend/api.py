import requests

API_BASE = "http://localhost:8000"


def list_equities(token):
    url = f"{API_BASE}/equities/list"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    return resp.json() if resp.status_code == 200 else []


def search_equities(token, query):
    url = f"{API_BASE}/equities/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"query": query}
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    return resp.json() if resp.status_code == 200 else []
