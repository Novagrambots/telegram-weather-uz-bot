"""Конфигурация бота — все настройки из .env"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # токен бота
    bot_token: str

    # PostgreSQL
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "bot_4_weather_uz"
    db_user: str = "bot_4_weather_uz"
    db_password: str = ""

    # юзернейм бота
    bot_username: str = ""

    # админы бота (через запятую в .env)
    admin_ids: str = ""
    admin_username: str = "admin"

    # часовой пояс
    timezone: str = "Asia/Tashkent"

    # OpenWeatherMap API
    owm_api_key: str = ""
    owm_base: str = "https://api.openweathermap.org/data/2.5"
    owm_geo_base: str = "https://api.openweathermap.org/geo/1.0"

    # WeatherAPI (резервный провайдер)
    weatherapi_key: str = ""

    # TTL кэша (минуты)
    cache_current_ttl_min: int = 10
    cache_forecast_ttl_min: int = 60

    @property
    def admin_id_list(self) -> list[int]:
        """Парсит admin_ids из строки в список int"""
        if not self.admin_ids:
            return []
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]

    @property
    def db_url(self) -> str:
        """URL для подключения к PostgreSQL через asyncpg"""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# глобальный экземпляр настроек
settings = Settings()
