import os

SECRET_KEY = os.getenv("SECRET_KEY", "reviewsense-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reviewsense.db")
