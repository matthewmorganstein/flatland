from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    RISE: str = "RISE API"
    RISE_SIGNALS: str = "Rise Signals Database"
    V1: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    MONGO_URI: str = os.getenv("MONGO_URI")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME")
    PORT: int = int(os.getenv("PORT", 8000))
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    API_KEY: str = os.getenv("API_KEY")
    TWELVE_DATA_API_KEY: str = os.getenv("TWELVE_DATA_API_KEY")
    RISE_APP_URL: str = os.getenv("RISE_APP_URL", "http://localhost:5000")
    RATE_LIMIT_MAX: int = int(os.getenv("RATE_LIMIT_MAX", 100))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", 3600))

settings = Settings()
