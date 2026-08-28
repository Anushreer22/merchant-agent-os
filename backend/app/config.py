from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "Merchant Agent OS"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    RAZORPAY_KEY_ID: str = Field(default="", env="RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET: str = Field(default="", env="RAZORPAY_KEY_SECRET")
    RAZORPAY_WEBHOOK_SECRET: str = Field(default="", env="RAZORPAY_WEBHOOK_SECRET")
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    LLM_MODEL: str = Field(default="gpt-4o-mini", env="LLM_MODEL")
    PAYMENT_RETRY_LIMIT: int = Field(default=2, env="PAYMENT_RETRY_LIMIT")
    PAYMENT_RETRY_DELAY_SECONDS: int = Field(default=1, env="PAYMENT_RETRY_DELAY_SECONDS")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
