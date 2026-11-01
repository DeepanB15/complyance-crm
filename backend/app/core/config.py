from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str

    zoho_client_id: str
    zoho_client_secret: str
    zoho_refresh_token: str
    zoho_organization_id: str = ""

    zoho_accounts_url: str = "https://accounts.zoho.in"
    zoho_api_url: str = "https://www.zohoapis.in/books/v3"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()