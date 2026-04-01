
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY     = os.getenv("SECRET_KEY", "dev-secret")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    USE_AI = os.getenv("USE_AI", "false").lower().strip() == "true"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}