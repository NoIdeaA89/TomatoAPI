import os


def _lista(valor: str) -> list[str]:
    return [v.strip() for v in valor.split(",") if v.strip()]


class Settings:
    """Configuración leída desde variables de entorno."""

    def __init__(self) -> None:
        url = os.getenv("DATABASE_URL", "sqlite:///./tomatoapi.db")
        # Algunos proveedores entregan "postgres://", SQLAlchemy exige "postgresql://".
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        self.database_url = url

        # En producción SIEMPRE define SECRET_KEY (ej. en Render). El valor por defecto es solo para desarrollo.
        self.secret_key = os.getenv("SECRET_KEY", "dev-only-insecure-secret-change-me-please")
        self.access_token_minutes = int(os.getenv("ACCESS_TOKEN_MINUTES", "1440"))

        self.cors_origins = _lista(
            os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
        )

        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.forecast_url = "https://api.open-meteo.com/v1/forecast"


settings = Settings()
