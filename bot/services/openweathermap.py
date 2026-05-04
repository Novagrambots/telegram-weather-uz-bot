"""Клиент OpenWeatherMap API.

Эндпоинты:
  /data/2.5/weather       — текущая
  /data/2.5/forecast      — прогноз 5 дней / 3 часа
  /data/2.5/air_pollution — качество воздуха
  /geo/1.0/direct         — геокодинг
  /geo/1.0/reverse        — обратный геокодинг
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from bot.config import settings

logger = logging.getLogger(__name__)


class OWMError(Exception):
    """Ошибка OpenWeatherMap API"""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(f"[{status}] {message}")
        self.status = status
        self.message = message


class OWMQuotaError(OWMError):
    """Превышен лимит запросов (429) или ключ недействителен (401)"""


class OWMNotFound(OWMError):
    """Ресурс/город не найден (404)"""


class OpenWeatherMapClient:
    """Async-клиент с глобальным семафором (10 параллельных запросов)."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openweathermap.org/data/2.5",
        geo_url: str = "https://api.openweathermap.org/geo/1.0",
        timeout: float = 10.0,
        max_concurrent: int = 10,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.geo_url = geo_url.rstrip("/")
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

    async def _request(self, url: str, params: dict[str, Any]) -> Any:
        """Универсальный GET с ретраями. Возвращает dict или list (geo возвращает list)."""
        if not self.api_key:
            raise OWMError(0, "OWM_API_KEY не задан")

        params = dict(params)
        params["appid"] = self.api_key

        async with self._sem:
            client = await self._get_client()
            attempt = 0
            last_exc: Exception | None = None
            while attempt < 3:
                attempt += 1
                try:
                    resp = await client.get(url, params=params)
                except (httpx.TimeoutException, httpx.NetworkError) as e:
                    last_exc = e
                    await asyncio.sleep(0.5 * attempt)
                    continue

                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code in (401, 429):
                    raise OWMQuotaError(resp.status_code, resp.text)
                if resp.status_code == 404:
                    raise OWMNotFound(404, resp.text)
                if resp.status_code >= 500:
                    last_exc = OWMError(resp.status_code, resp.text)
                    await asyncio.sleep(0.5 * attempt)
                    continue
                raise OWMError(resp.status_code, resp.text)

            if last_exc:
                raise OWMError(0, str(last_exc))
            raise OWMError(0, "unknown")

    # === Погода ===

    async def get_current(
        self,
        *,
        city: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        lang: str = "ru",
        units: str = "metric",
    ) -> dict:
        params: dict[str, Any] = {"lang": lang, "units": units}
        if city:
            params["q"] = city
        elif lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon
        else:
            raise ValueError("Нужны city или lat/lon")
        return await self._request(f"{self.base_url}/weather", params)

    async def get_forecast(
        self,
        *,
        city: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        lang: str = "ru",
        units: str = "metric",
    ) -> dict:
        params: dict[str, Any] = {"lang": lang, "units": units}
        if city:
            params["q"] = city
        elif lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon
        else:
            raise ValueError("Нужны city или lat/lon")
        return await self._request(f"{self.base_url}/forecast", params)

    async def get_air_pollution(self, *, lat: float, lon: float) -> dict:
        params = {"lat": lat, "lon": lon}
        return await self._request(f"{self.base_url}/air_pollution", params)

    async def geocode(self, query: str, *, limit: int = 5) -> list[dict]:
        params = {"q": query, "limit": limit}
        url = f"{self.geo_url}/direct"
        try:
            data = await self._request(url, params)
        except OWMNotFound:
            return []
        return data or []

    async def reverse_geocode(
        self, lat: float, lon: float, *, limit: int = 1
    ) -> list[dict]:
        params = {"lat": lat, "lon": lon, "limit": limit}
        url = f"{self.geo_url}/reverse"
        try:
            data = await self._request(url, params)
        except OWMNotFound:
            return []
        return data or []

# глобальный экземпляр
owm_client = OpenWeatherMapClient(
    api_key=settings.owm_api_key,
    base_url=settings.owm_base,
    geo_url=settings.owm_geo_base,
)
