from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application Configuration
    Loads variables from .env file
    """
    DATABASE_URL: str
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "employee_logs"

    class Config:
        env_file = ".env"

settings = Settings()
