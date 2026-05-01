import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Job Application Intelligence Assistant"
    DEBUG: bool = True
    
    # Weights for overall match score
    WEIGHT_SKILLS: float = 0.4
    WEIGHT_EXPERIENCE: float = 0.4
    WEIGHT_KEYWORDS: float = 0.2
    
    # LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = "gpt-3.5-turbo" # Default model
    
    # NLP Settings
    SPACY_MODEL: str = "en_core_web_sm"

settings = Settings()
