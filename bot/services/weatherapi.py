"""Резервный клиент WeatherAPI.com.

Документация: https://www.weatherapi.com/docs/
Используется только когда OpenWeatherMap недоступен.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from bot.config import settings

logger = logging.getLogger(__name__)


class WeatherAPIError(Exception):
    pass


class WeatherAPIClient:
    """Минимальный async-клиент WeatherAPI.com."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.weatherapi.com/v1",
        timeout: float = 10.0,
        max_concurrent: int = 5,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._sem = asyncio.Semaphore(max_concurrent)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _request(self, path: str, params: dict[str, Any]) -> dict:
        if not self.api_key:
            raise WeatherAPIError("WEATHERAPI_KEY не задан")
        params = dict(params)
        params["key"] = self.api_key
        async with self._sem:
            client = await self._get_client()
            try:
                resp = await client.get(f"{self.base_url}{path}", params=params)
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                raise WeatherAPIError(f"network: {e}")
            if resp.status_code == 200:
                return resp.json()
            raise WeatherAPIError(f"[{resp.status_code}] {resp.text}")

    async def get_current(
        self, *, q: str, lang: str = "ru"
    ) -> dict:
        return await self._request("/current.json", {"q": q, "lang": lang})

    async def get_forecast(
        self, *, q: str, days: int = 5, lang: str = "ru"
    ) -> dict:
        return await self._request(
            "/forecast.json", {"q": q, "days": days, "lang": lang, "alerts": "yes"}
        )


weatherapi_client = WeatherAPIClient(api_key=settings.weatherapi_key)
