from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api import auth, creators, brands, jobs, upload
from .database import engine, Base

# Create tables (For dev only. In prod use alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(creators.router, prefix=f"{settings.API_V1_STR}/creators", tags=["creators"])
app.include_router(brands.router, prefix=f"{settings.API_V1_STR}/brands", tags=["brands"])
app.include_router(jobs.router, prefix=f"{settings.API_V1_STR}/jobs", tags=["jobs"])
app.include_router(upload.router, prefix=f"{settings.API_V1_STR}/upload", tags=["upload"])

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}
