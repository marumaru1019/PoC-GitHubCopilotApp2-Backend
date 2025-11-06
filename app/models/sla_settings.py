from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime

from app.db.base import Base


class SLASettings(Base):
    __tablename__ = "sla_settings"

    id = Column(String, primary_key=True)
    priority = Column(String, unique=True, nullable=False)  # LOW, MEDIUM, HIGH, URGENT
    first_response_target_minutes = Column(Integer, nullable=False)
    resolution_target_minutes = Column(Integer, nullable=False)
    pause_on_waiting_customer = Column(Boolean, default=True, nullable=False)
    timezone = Column(String, default="Asia/Tokyo", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
