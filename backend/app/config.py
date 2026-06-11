from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Tú Marketing"
    APP_ENV: str = "development"
    SECRET_KEY: str
    DEBUG: bool = False

    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    REDIS_URL: str = "redis://localhost:6379"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    SEPAY_API_KEY: str = ""
    SEPAY_WEBHOOK_SECRET: str = ""
    BANK_ACCOUNT_NUMBER: str = ""
    BANK_NAME: str = "Vietcombank"
    BANK_ACCOUNT_NAME: str = ""
    ORDER_EXPIRE_MINUTES: int = 30

    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "hello@tumarketing.vn"
    EMAIL_FROM_NAME: str = "Tú Marketing"

    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "eduvietpro"
    R2_PUBLIC_URL: str = ""

    GOOGLE_SERVICE_ACCOUNT_JSON: str = "./google-service-account.json"
    GOOGLE_SHEET_ID: str = ""
    GOOGLE_SHEET_NAME: str = "Leads"

    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    TZ: str = "Asia/Ho_Chi_Minh"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
