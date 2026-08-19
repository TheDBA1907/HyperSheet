import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, BigInteger, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import BaseModel


class Dataset(BaseModel):
    __tablename__ = "datasets"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
        index=True,
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    source_name: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )

    source_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="active",
    )

    row_count: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    column_count: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    refresh_mode: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="manual",
    )

    last_refresh_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    extra_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )