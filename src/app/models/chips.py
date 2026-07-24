from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from src.app.core.database import Base


class Chips(Base):
    __tablename__ = "chips"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
