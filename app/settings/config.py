from pathlib import Path
from typing import Annotated

from pydantic import PostgresDsn, SecretStr, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

BASEDIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # App
    APP_TITLE: str = 'SpaceX ETL'
    APP_DESCRIPTION: str = 'Default description'
    DEBUG: bool = False
    LOG_LEVEL: str = 'INFO'

    # Postgres
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_PORT: int
    POSTGRES_DSN: PostgresDsn | str = ''

    # Data Source
    DATA_SOURCE_URL: str = 'https://spacex-production.up.railway.app/'

    model_config = SettingsConfigDict(env_file=BASEDIR / '.env')

    @field_validator('POSTGRES_DSN')
    def build_postgres_dsn(cls, value: PostgresDsn | None, info: ValidationInfo) -> Annotated[str, PostgresDsn]:
        if not value:
            value = PostgresDsn.build(
                scheme='postgresql+asyncpg',
                username=info.data['POSTGRES_USER'],
                password=info.data['POSTGRES_PASSWORD'].get_secret_value(),
                host=info.data['POSTGRES_HOST'],
                port=info.data['POSTGRES_PORT'],
                path=f"{info.data['POSTGRES_DB'] or ''}",
            )
        return str(value)


app_settings = Settings()
