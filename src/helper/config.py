from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuration settings for the application.
    """

    # Example configuration variables
    APP_NAME: str 
    APP_VERSION: str

    FILE_ALLOWED_TYPES: list
    FILE_ALLOWED_SIZE_MB: int
    FILE_DEFAULT_CHUNK_SIZE: int

    MONGODB_URL: str
    MONGODB_DATABASE: str

    GENERATION_BACKEND: str 
    EMBEDDING_BACKEND:str

    OPENAI_API_KEY: str
    OPENAI_API_URL: str 
    COHERE_API_KEY: str

    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None

    INPUT_DAFAULT_MAX_CHARACTERS: int = None
    GENERATION_DAFAULT_MAX_TOKENS: int = None
    GENERATION_DAFAULT_TEMPERATURE: float = None
    class Config:
        env_file = ".env"  # Load environment variables from a .env file
 

def get_settings() -> Settings:
    """
    Get the application settings.

    Returns:
        Settings: The application settings.
    """
    return Settings()