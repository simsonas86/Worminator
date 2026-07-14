from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    twitch_app_id: str
    twitch_app_secret: SecretStr
    twitch_superadmin_id: int = 0
    target_channel: str

    db_user: str
    db_password: SecretStr
    db_database: str
    db_host: str
    db_port: int

    obs_ip: str | None = None
    obs_port: int | None = None
    obs_password: SecretStr | None = None

    overlay_ws_disabled: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        frozen=True,
        env_ignore_empty=True,
    )


settings = Settings()
