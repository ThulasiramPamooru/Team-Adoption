import httpx
from flowguard.utils.config import get_api_url, load_token
from rich.console import Console

console = Console()


def get_headers() -> dict:
    token = load_token()
    if not token:
        console.print("[red]No auth token found. Set FLOWGUARD_TOKEN env var.[/]")
    return {"Authorization": f"Bearer {token}"} if token else {}


def get(path: str, **kwargs) -> dict:
    url = f"{get_api_url()}/api/v1{path}"
    with httpx.Client(headers=get_headers(), timeout=30) as client:
        resp = client.get(url, **kwargs)
        resp.raise_for_status()
        return resp.json()


def post(path: str, **kwargs) -> dict:
    url = f"{get_api_url()}/api/v1{path}"
    with httpx.Client(headers=get_headers(), timeout=60) as client:
        resp = client.post(url, **kwargs)
        resp.raise_for_status()
        return resp.json()
