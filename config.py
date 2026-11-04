"""
config.py
---------
Centralised settings for VYNERA AI.
All environment variables are read once here and imported everywhere else.
"""
 
from pydantic_settings import BaseSettings
from functools import lru_cache
 
 
class Settings(BaseSettings):
    # MongoDB
    mongo_uri: str = "mongodb+srv://reddycherish76:Cherish1302@dataleak.zr189.mongodb.net/"
    mongo_db_name: str = "vynera"

    # JWT
    jwt_secret: str = "change_me"
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 7
 
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
 
    # Model
    model_dir: str = "./models"
    tokenizer_path: str = "./models/tokenizer.json"
 
    # Self-learning scheduler
    self_learn_hour: int = 3
    self_learn_min_feedback: int = 50
 
    # Safety
    crisis_hotline: str = "iCall (India): 9152987821 | Vandrevala Foundation: 1860-2662-345"
 
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "protected_namespaces": ("settings_",),
    }
 
 
@lru_cache()
def get_settings() -> Settings:
    return Settings()
 
 
settings = get_settings()
 