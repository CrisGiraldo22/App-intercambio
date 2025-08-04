from datetime import timezone
from email.policy import default

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Enum, column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base



class UserRole(str, enum.Enum):
    NANNY = "nanny"
    FAMILY = "family"

class RequestStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CAnCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.NANNY)
    bio = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    update_at = Column(DateTime(timezone=True), onupdate=func.now())

    #Relationships
    request = relationship("Request", back_populates="user")
    sessions_as_family = relationship("session", foreign_keys="session.family_id", back_populates="family")
    sessions_as_nanny =  relationship("session", foreign_keys="session.nanny_id", back_populates="nanny")
    ratings_given = relationship("Rating", foreign_keys="Rating.rater_id", back_populates="rater")
    ratings_received = relationship("Rating", foreign_keys="Rating.rated_id", back_populates="rated")

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(String)
    location = Column(String, nullable=False)
    hourly_rate = Column(Float, nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.OPEN)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    update_at = Column(DateTime(timezone=True), onupdate=func.now())

    #Relationships
    user = relationship("User", back_populates="requests")
    session = relationship("Session", back_populates="requests")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("request.id"))
    family_id = Column(Integer, ForeignKey("users.id"))
    nanny_id = Column(Integer, ForeignKey("users.id"))
    star_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    hourly_rate = Column(Float, nullable=False)
    status = Column(String, default="scheduled")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    #Relationships
    request = relationship("Request", back_populates="sessions")
    family = relationship("User", foreign_keys=[family_id], back_populates="sessions_as_family")
    nanny = relationship("User", foreign_keys=[nanny_id], back_populates="sessions_as_nanny")

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    rater_id = Column(Integer, ForeignKey("users.id"))
    rated_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("session.id"), nullable=True)
    rating = Column(Integer, nullable=True) # 1-5 stars
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())









