from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    use_in_memory_db: bool = True
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/aws_try_out"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
