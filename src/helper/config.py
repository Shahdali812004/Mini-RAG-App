from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuration settings for the application.
    """

    # Example configuration variables
    APP_NAME: str 
    APP_VERSION: str
    OPENAI_API_KEY: str
    FILE_ALLOWED_TYPES: list
    FILE_ALLOWED_SIZE_MB: int
    FILE_DEFAULT_CHUNK_SIZE: int
    MONGODB_URL: str
    MONGODB_DATABASE: str
    class Config:
        env_file = ".env"  # Load environment variables from a .env file
 

def get_settings() -> Settings:
    """
    Get the application settings.

    Returns:
        Settings: The application settings.
    """
    return Settings()