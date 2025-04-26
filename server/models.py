from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, declarative_base
from database import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())


class Dialog(Base):
    __tablename__ = "dialogs"
    dialog_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    name = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    messages = relationship("Message", back_populates="dialog")


class Message(Base):
    __tablename__ = "messages"
    message_id = Column(Integer, primary_key=True)
    dialog_id = Column(Integer, ForeignKey("dialogs.dialog_id", ondelete="CASCADE"))
    type = Column(String(50))
    text = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    dialog = relationship("Dialog", back_populates="messages")


class MessageUserReview(Base):
    __tablename__ = "message_user_reviews"
    message_id = Column(Integer, ForeignKey("messages.message_id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    is_positive = Column(Boolean)
    created_at = Column(DateTime, server_default=func.now())


class DialogShare(Base):
    __tablename__ = "dialog_shares"
    share_id = Column(Integer, primary_key=True)
    dialog_id = Column(Integer, ForeignKey("dialogs.dialog_id", ondelete="CASCADE"))
    created_at = Column(DateTime, server_default=func.now())
