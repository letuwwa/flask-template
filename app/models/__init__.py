# Import models here so Flask-Migrate sees them in db.metadata.
from .user import User, UserRole
from .token_blocklist import TokenBlocklist

__all__ = ("TokenBlocklist", "User", "UserRole")
