from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from auth import get_password_hash


# ─── User CRUD ────────────────────────────────────────────────────────────────
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    stmt = select(models.User).where(models.User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_name(db: AsyncSession, name: str) -> Optional[models.User]:
    stmt = select(models.User).where(models.User.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_in: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user_in.password)
    db_user = models.User(
        email=user_in.email,
        password_hash=hashed_password,
        name=getattr(user_in, "name", None)
    )
    db.add(db_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(db_user)
    return db_user


# ─── Dialog CRUD ──────────────────────────────────────────────────────────────
async def get_dialogs_by_user(db: AsyncSession, user_id: int) -> List[models.Dialog]:
    stmt = select(models.Dialog).where(models.Dialog.user_id == user_id).order_by(models.Dialog.created_at)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_dialog_by_id(db: AsyncSession, dialog_id: int) -> Optional[models.Dialog]:
    stmt = select(models.Dialog).where(models.Dialog.dialog_id == dialog_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_dialog(db: AsyncSession, user_id: int, name: str) -> models.Dialog:
    db_dialog = models.Dialog(user_id=user_id, name=name)
    db.add(db_dialog)
    await db.commit()
    await db.refresh(db_dialog)
    return db_dialog


# ─── Message CRUD ─────────────────────────────────────────────────────────────
async def get_messages_by_dialog(db: AsyncSession, dialog_id: int) -> List[models.Message]:
    stmt = (
        select(models.Message)
        .where(models.Message.dialog_id == dialog_id)
        .order_by(models.Message.created_at)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_message(
    db: AsyncSession,
    msg_in: schemas.MessageCreate,
    is_bot: bool = False
) -> models.Message:
    db_msg = models.Message(
        dialog_id=msg_in.dialog_id,
        text=msg_in.text,
        type="bot" if is_bot else "user",
    )
    db.add(db_msg)
    await db.commit()
    await db.refresh(db_msg)
    return db_msg


# ─── Message Review CRUD ─────────────────────────────────────────────────────
async def get_user_review(
    db: AsyncSession,
    message_id: int,
    user_id: int
) -> Optional[models.MessageUserReview]:
    stmt = select(models.MessageUserReview).where(
        (models.MessageUserReview.message_id == message_id) &
        (models.MessageUserReview.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_message_review(
    db: AsyncSession,
    message_id: int,
    user_id: int,
    is_positive: bool
) -> models.MessageUserReview:
    db_review = models.MessageUserReview(
        message_id=message_id,
        user_id=user_id,
        is_positive=is_positive,
    )
    db.add(db_review)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # если отзыв уже есть, обновляем через merge
        await db.merge(db_review)
        await db.commit()
    await db.refresh(db_review)
    return db_review


# ─── Dialog Share CRUD ────────────────────────────────────────────────────────
async def create_dialog_share(db: AsyncSession, dialog_id: int) -> models.DialogShare:
    db_share = models.DialogShare(dialog_id=dialog_id)
    db.add(db_share)
    await db.commit()
    await db.refresh(db_share)
    return db_share

async def get_dialog_share(db: AsyncSession, share_id: int) -> Optional[models.DialogShare]:
    stmt = select(models.DialogShare).where(models.DialogShare.share_id == share_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_messages_by_user(db: AsyncSession, user_id: int) -> list[models.Message]:
    stmt = (
        select(models.Message)
        .join(models.Dialog, models.Message.dialog_id == models.Dialog.dialog_id)
        .where(models.Dialog.user_id == user_id)
        .order_by(models.Message.created_at)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
