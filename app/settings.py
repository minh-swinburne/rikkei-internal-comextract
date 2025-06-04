from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings(BaseSettings):
    openrouter_api_key: str
    openrouter_base_url: str
    openrouter_model: str
    
settings = Settings()