from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from jose import jwt, JWTError
from functools import lru_cache
from typing import Optional
from app.core.config import get_settings

settings = get_settings()
security = HTTPBearer(auto_error=False)

# ── DEV_MODE fake admin user ───────────────────
DEV_USER = {
    "sub": "dev|local-admin",
    "email": "admin@localhost.dev",
    "name": "Local Dev Admin",
    "picture": None,
    "https://flowguard/roles": ["admin", "developer"],
}


@lru_cache(maxsize=1)
def get_jwks() -> dict:
    """Fetch Auth0 JWKS (cached)."""
    url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
    with httpx.Client() as client:
        resp = client.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()


def verify_token(token: str) -> dict:
    """Validate an Auth0 JWT and return the decoded payload."""
    # DEV_MODE: accept the magic dev token without hitting Auth0
    if settings.dev_mode and token == "dev-local-token":
        return DEV_USER
    try:
        jwks = get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks.get("keys", []):
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
        if not rsa_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token key")

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=settings.auth0_algorithms,
            audience=settings.auth0_audience,
            issuer=f"https://{settings.auth0_domain}/",
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """FastAPI dependency — returns decoded JWT payload.
    In DEV_MODE, returns a fake admin user when no token is provided.
    """
    if settings.dev_mode and credentials is None:
        return DEV_USER
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return verify_token(credentials.credentials)


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """FastAPI dependency — enforces admin role."""
    roles: list[str] = current_user.get("https://flowguard/roles", [])
    if "admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user
