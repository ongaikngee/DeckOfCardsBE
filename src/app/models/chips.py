from src.app.core.database import Base
from sqlalchemy import Column, Integer, String  

class Chips(Base):
    __tablename__ = 'chips'
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, nullable=False)
    user_id = Column(Integer, foreign_key='users.id', nullable=False)
    reason = Column(String, nullable=True)
    
    
