from pathlib import Path

from pydantic_settings import SettingsConfigDict, BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class ProjectSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding='utf-8',
        extra='ignore'
    )
    #DB
    db_user: str
    db_port: int
    db_password: str
    db_host: str
    db_name: str
    db_show_query: bool
    api_key: str

    @property
    def get_postgres_url_sync(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def get_postgres_url_async(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

def get_settings() -> ProjectSettings:
    """Возвращает общие настройки приложения"""
    return ProjectSettings()

settings = get_settings()

