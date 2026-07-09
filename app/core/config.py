from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Reelfy"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-this-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/reelfy")
    
    # Efí
    EFI_CLIENT_ID: str = os.getenv("EFI_CLIENT_ID", "")
    EFI_CLIENT_SECRET: str = os.getenv("EFI_CLIENT_SECRET", "")
    EFI_CERTIFICATE_PATH: str = os.getenv("EFI_CERTIFICATE_PATH", "")

    # AWS S3
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION_NAME: str = os.getenv("AWS_REGION_NAME", "us-east-1")
    AWS_BUCKET_NAME: str = os.getenv("AWS_BUCKET_NAME", "vidbly-videos-staging")

    class Config:
        case_sensitive = True

settings = Settings()
