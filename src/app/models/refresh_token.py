from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from src.app.core.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    token_hash = Column(String, nullable=False, unique=True,)
    created_at = Column(DateTime(timezone=True), server_default=func.now(),)
    expired_at = Column(DateTime(timezone=True), nullable=False,)
    revoked_at = Column(DateTime(timezone=True), nullable=True,)
