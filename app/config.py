import os


class Config:
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://admin:admin@localhost:5433/mydb",
    )
