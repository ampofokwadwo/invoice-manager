from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Invoice Manager"
    DATABASE_URL: str = "sqlite:///./invoice_manager.db"

settings = Settings()


