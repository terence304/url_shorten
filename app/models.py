"""SQLAlchemy ORM models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# BigInteger for PostgreSQL, Integer for SQLite (which needs INTEGER for autoincrement)
BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    urls: Mapped[list[URL]] = relationship(back_populates="owner", lazy="selectin")


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    short_key: Mapped[str] = mapped_column(String(7), unique=True, index=True, nullable=True)
    long_url: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    custom_alias: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    owner: Mapped[User | None] = relationship(back_populates="urls")
    clicks: Mapped[list[Click]] = relationship(back_populates="url", lazy="selectin")


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    url_id: Mapped[int] = mapped_column(ForeignKey("urls.id"), nullable=False, index=True)
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    referrer: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)

    url: Mapped[URL] = relationship(back_populates="clicks")

    __table_args__ = (
        Index("ix_clicks_url_id_clicked_at", "url_id", "clicked_at"),
    )
