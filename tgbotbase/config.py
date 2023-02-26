from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/postgres'

    bot_token: str = '5693124495:AAGBRnfIcUpQnGL9ieeg5p9c6mLwD9r5e04'

    media_root: str = '../media/'


settings = Settings(
    _env_file='.env',
    _env_file_encoding='utf-8'
)
