# Import models here so Flask-Migrate sees them in db.metadata.
from .user import User

__all__ = ("User",)
