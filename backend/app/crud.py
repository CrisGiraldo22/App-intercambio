from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from . import models, schemas
from .auth import get_password_hash


# User CRUD operations
async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role,
        bio=user.bio,
        location=user.location,
        phone=user.phone
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(
        select(models.User).where(models.User.username == username)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(models.User).where(models.User.email == email)
    )
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.User).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_user(db: AsyncSession, user_id: int, user_update: schemas.UserUpdate):
    update_data = user_update.dict(exclude_unset=True)
    if update_data:
        await db.execute(
            update(models.User)
            .where(models.User.id == user_id)
            .values(**update_data)
        )
        await db.commit()
    return await get_user_by_id(db, user_id)


# Request CRUD operations
async def create_request(db: AsyncSession, request: schemas.RequestCreate, user_id: int):
    db_request = models.Request(**request.dict(), user_id=user_id)
    db.add(db_request)
    await db.commit()
    await db.refresh(db_request)
    return db_request


async def get_request(db: AsyncSession, request_id: int):
    result = await db.execute(
        select(models.Request)
        .options(selectinload(models.Request.user))
        .where(models.Request.id == request_id)
    )
    return result.scalar_one_or_none()


async def get_requests(db: AsyncSession, skip: int = 0, limit: int = 100, status: Optional[str] = None):
    query = select(models.Request).options(selectinload(models.Request.user))
    if status:
        query = query.where(models.Request.status == status)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def update_request(db: AsyncSession, request_id: int, request_update: schemas.RequestUpdate):
    update_data = request_update.dict(exclude_unset=True)
    if update_data:
        await db.execute(
            update(models.Request)
            .where(models.Request.id == request_id)
            .values(**update_data)
        )
        await db.commit()
    return await get_request(db, request_id)


async def delete_request(db: AsyncSession, request_id: int):
    await db.execute(delete(models.Request).where(models.Request.id == request_id))
    await db.commit()


# Session CRUD operations
async def create_session(db: AsyncSession, session: schemas.SessionCreate):
    db_session = models.Session(**session.dict())
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session


async def get_session(db: AsyncSession, session_id: int):
    result = await db.execute(
        select(models.Session)
        .options(
            selectinload(models.Session.request),
            selectinload(models.Session.mentor),
            selectinload(models.Session.apprentice)
        )
        .where(models.Session.id == session_id)
    )
    return result.scalar_one_or_none()


async def get_user_sessions(db: AsyncSession, user_id: int, role: Optional[str] = None):
    query = select(models.Session).options(
        selectinload(models.Session.request),
        selectinload(models.Session.mentor),
        selectinload(models.Session.apprentice)
    )
    if role == "mentor":
        query = query.where(models.Session.mentor_id == user_id)
    elif role == "apprentice":
        query = query.where(models.Session.apprentice_id == user_id)
    else:
        query = query.where(
            (models.Session.mentor_id == user_id) | (models.Session.apprentice_id == user_id)
        )
    result = await db.execute(query)
    return result.scalars().all()


async def update_session(db: AsyncSession, session_id: int, session_update: schemas.SessionUpdate):
    update_data = session_update.dict(exclude_unset=True)
    if update_data:
        await db.execute(
            update(models.Session)
            .where(models.Session.id == session_id)
            .values(**update_data)
        )
        await db.commit()
    return await get_session(db, session_id)


# Rating CRUD operations
async def create_rating(db: AsyncSession, rating: schemas.RatingCreate, rater_id: int):
    db_rating = models.Rating(**rating.dict(), rater_id=rater_id)
    db.add(db_rating)
    await db.commit()
    await db.refresh(db_rating)
    return db_rating


async def get_user_ratings(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.Rating)
        .options(
            selectinload(models.Rating.rater),
            selectinload(models.Rating.rated)
        )
        .where(models.Rating.rated_id == user_id)
    )
    return result.scalars().all()


async def get_user_rating_stats(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.Rating).where(models.Rating.rated_id == user_id)
    )
    ratings = result.scalars().all()
    if not ratings:
        return {"average_rating": 0, "total_ratings": 0}

    total_rating = sum(r.rating for r in ratings)
    average_rating = total_rating / len(ratings)
    return {"average_rating": round(average_rating, 2), "total_ratings": len(ratings)} 