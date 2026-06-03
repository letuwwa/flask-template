import os


class Config:
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
