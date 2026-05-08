from dataclasses import dataclass
from os import getenv


DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
)


def _parse_csv_env(value: str | None, default: tuple[str, ...]) -> list[str]:
    if value is None:
        return list(default)
    origins = [item.strip() for item in value.split(",") if item.strip()]
    return origins or list(default)


@dataclass(frozen=True)
class Settings:
    cors_allow_origins: list[str]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] | None = None
    cors_allow_headers: list[str] | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            cors_allow_origins=_parse_csv_env(getenv("BACKEND_CORS_ORIGINS"), DEFAULT_CORS_ORIGINS),
            cors_allow_methods=["*"],
            cors_allow_headers=["*"],
        )


settings = Settings.from_env()
