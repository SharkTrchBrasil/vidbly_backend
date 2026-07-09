from pydantic_settings import BaseSettings
import os
import json
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def get_aws_secrets(secret_name="prod/vidbly/credentials", region_name="us-east-1"):
    region = os.getenv("AWS_REGION", region_name)
    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region
        )
        response = client.get_secret_value(SecretId=secret_name)
        if 'SecretString' in response:
            return json.loads(response['SecretString'])
    except Exception as e:
        print(f"Warning: Could not load AWS Secrets from {secret_name}: {e}")
    return {}

# Carrega os segredos se estiver no ambiente de produção (ou se as chaves da AWS estiverem configuradas)
# Isso evita travamentos locais onde você pode não ter credenciais da AWS configuradas.
aws_secrets = {}
if os.getenv("ENVIRONMENT") == "production" or os.getenv("AWS_ACCESS_KEY_ID"):
    aws_secrets = get_aws_secrets()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Reelfy"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-this-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database & Redis
    DATABASE_URL: str = aws_secrets.get("DATABASE_URL", os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/reelfy"))
    REDIS_URL: str = aws_secrets.get("REDIS_URL", os.getenv("REDIS_URL", "redis://localhost:6379"))
    
    # Efí
    EFI_CLIENT_ID: str = os.getenv("EFI_CLIENT_ID", "")
    EFI_CLIENT_SECRET: str = os.getenv("EFI_CLIENT_SECRET", "")
    EFI_CERTIFICATE_PATH: str = os.getenv("EFI_CERTIFICATE_PATH", "")

    # AWS S3
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION_NAME: str = os.getenv("AWS_REGION_NAME", "us-east-1")
    AWS_BUCKET_NAME: str = os.getenv("AWS_BUCKET_NAME", "vidbly-videos-staging")
    
    # Stripe (Pega do AWS Secrets, e se não achar, usa do .env)
    STRIPE_SECRET_KEY: str = aws_secrets.get("STRIPE_SECRET_KEY", os.getenv("STRIPE_SECRET_KEY", ""))
    STRIPE_WEBHOOK_SECRET: str = aws_secrets.get("STRIPE_WEBHOOK_SECRET", os.getenv("STRIPE_WEBHOOK_SECRET", ""))
    STRIPE_PUBLISHABLE_KEY: str = aws_secrets.get("STRIPE_PUBLISHABLE_KEY", os.getenv("STRIPE_PUBLISHABLE_KEY", ""))

    class Config:
        case_sensitive = True

settings = Settings()
