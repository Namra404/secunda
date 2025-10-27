from fastapi import HTTPException, Header
from starlette import status

from configuration.base import settings


async def require_api_key(x_api_key: str | None = Header(None)):
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )