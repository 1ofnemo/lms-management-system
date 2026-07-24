from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://lms:lms@localhost:5432/lms"
    jwt_secret: str = "dev-secret-change-me"
    anthropic_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
