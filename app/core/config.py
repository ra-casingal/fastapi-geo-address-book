from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Address Book API"
    VERSION: str = "0.1.0"
    DATABASE_URL: str = "sqlite:///./address_book.db"

    class Config:
        env_file = ".env"


settings = Settings()
