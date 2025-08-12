from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .models import UserRole, RequestStatus


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: UserRole = UserRole.FAMILY
    bio: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Request schemas
class RequestBase(BaseModel):
    title: str
    description: str
    tags: Optional[str] = None
    location: str
    hourly_rate: Optional[float] = None


class RequestCreate(RequestBase):
    pass


class RequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    location: Optional[str] = None
    hourly_rate: Optional[float] = None
    status: Optional[RequestStatus] = None


class Request(RequestBase):
    id: int
    user_id: int
    status: RequestStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: User

    class Config:
        from_attributes = True


# Session schemas
class SessionBase(BaseModel):
    request_id: int
    mentor_id: int
    apprentice_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    hourly_rate: float
    status: str = "scheduled"
    notes: Optional[str] = None


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class Session(SessionBase):
    id: int
    created_at: datetime
    request: Request
    mentor: User
    apprentice: User

    class Config:
        from_attributes = True


# Rating schemas
class RatingBase(BaseModel):
    rated_id: int
    session_id: Optional[int] = None
    rating: int
    comment: Optional[str] = None


class RatingCreate(RatingBase):
    pass


class Rating(RatingBase):
    id: int
    rater_id: int
    created_at: datetime
    rater: User
    rated: User

    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Login schema
class Login(BaseModel):
    username: str
    password: str