from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    use_in_memory_db: bool = True
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/aws_try_out"
    )
    s3_bucket_name: str
    aws_region: str
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    s3_endpoint_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
