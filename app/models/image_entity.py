from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ImageMimeType(StrEnum):
    JPEG = "image/jpeg"
    PNG = "image/png"
    WEBP = "image/webp"


class ImageEntity(Base):
    __tablename__ = "note_images"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    note_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[ImageMimeType] = mapped_column(
        Enum(
            ImageMimeType,
            native_enum=False,
            create_constraint=False,
            length=100,
            validate_strings=True,
            values_callable=lambda mime_types: [
                mime_type.value for mime_type in mime_types
            ],
        ),
        nullable=False,
    )
    alt_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    object_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
