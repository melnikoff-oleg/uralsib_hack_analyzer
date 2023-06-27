from pydantic import BaseSettings


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = ""
    OPENAI_API_TOKEN: str = ""

    class Config:
        env_file = ".env"
