import uuid

from sqlalchemy import ForeignKey, String, Text, Integer, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import BaseModel


class Measure(BaseModel):
    __tablename__ = "measures"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)

    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    expression: Mapped[str] = mapped_column(Text, nullable=False)

    aggregation: Mapped[str | None] = mapped_column(String(50), nullable=True)

    format_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)

    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)

    decimal_places: Mapped[int | None] = mapped_column(Integer, nullable=True)

    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    extra_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        UniqueConstraint("dataset_id", "name", name="uq_measures_dataset_id_name"),
    )