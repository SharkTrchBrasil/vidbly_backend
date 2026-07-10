from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api import (
    auth, creators, brands, jobs, upload,
    job_applications, video_deliveries, video_revisions,
    reviews, payments, webhooks, notifications,
    chat, products, wallets, creator_tags, discover,
    chat_rooms, creator_wallet, favorites, disputes, portfolio
)
from .database import engine, Base
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.requests import Request

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Set all CORS enabled origins
allow_origins = ["*"]
if os.getenv("ENVIRONMENT") == "production":
    allow_origins = ["https://vidbly.com", "https://app.vidbly.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(creators.router, prefix=f"{settings.API_V1_STR}/creators", tags=["creators"])
app.include_router(brands.router, prefix=f"{settings.API_V1_STR}/brands", tags=["brands"])
app.include_router(jobs.router, prefix=f"{settings.API_V1_STR}/jobs", tags=["jobs"])
app.include_router(upload.router, prefix=f"{settings.API_V1_STR}/upload", tags=["upload"])
app.include_router(job_applications.router, prefix=f"{settings.API_V1_STR}/applications", tags=["applications"])
app.include_router(video_deliveries.router, prefix=f"{settings.API_V1_STR}/deliveries", tags=["deliveries"])
app.include_router(video_revisions.router, prefix=f"{settings.API_V1_STR}/revisions", tags=["revisions"])
app.include_router(reviews.router, prefix=f"{settings.API_V1_STR}/reviews", tags=["reviews"])
app.include_router(payments.router, prefix=f"{settings.API_V1_STR}/payments", tags=["payments"])
app.include_router(webhooks.router, prefix=f"{settings.API_V1_STR}/webhooks", tags=["webhooks"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["notifications"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
app.include_router(products.router, prefix=f"{settings.API_V1_STR}/products", tags=["products"])
app.include_router(wallets.router, prefix=f"{settings.API_V1_STR}/wallet", tags=["wallet"])
app.include_router(creator_tags.router, prefix=f"{settings.API_V1_STR}/tags", tags=["tags"])
app.include_router(discover.router, prefix=f"{settings.API_V1_STR}/discover", tags=["discover"])
app.include_router(chat_rooms.router, prefix=f"{settings.API_V1_STR}/chat-rooms", tags=["chat"])
app.include_router(creator_wallet.router, prefix=f"{settings.API_V1_STR}/creator-wallet", tags=["wallet"])
app.include_router(favorites.router, prefix=f"{settings.API_V1_STR}/favorites", tags=["favorites"])
app.include_router(disputes.router, prefix=f"{settings.API_V1_STR}/disputes", tags=["disputes"])
app.include_router(portfolio.router, prefix=f"{settings.API_V1_STR}/portfolio", tags=["portfolio"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
@limiter.limit("10/minute")
def root(request: Request):
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}
