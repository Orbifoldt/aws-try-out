import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.image_entity import ImageEntity
from app.settings import Settings

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client
else:
    from botocore.client import BaseClient as S3Client


@dataclass(frozen=True, slots=True)
class ImageContent:
    metadata: ImageEntity
    content: bytes


class ImageStorage(ABC):
    @abstractmethod
    async def store_image(self, image: ImageEntity, content: bytes) -> ImageEntity:
        ...

    @abstractmethod
    async def get_image(self, note_id: UUID, image_id: UUID) -> ImageContent:
        ...

    @abstractmethod
    async def list_images(self, note_id: UUID) -> list[ImageEntity]:
        ...


class InMemoryImageStorage(ImageStorage):
    def __init__(self) -> None:
        self._images: dict[UUID, dict[UUID, tuple[ImageEntity, bytes]]] = {}

    async def store_image(self, image: ImageEntity, content: bytes) -> ImageEntity:
        self._images.setdefault(image.note_id, {})[image.id] = (image, content)
        return image

    async def get_image(self, note_id: UUID, image_id: UUID) -> ImageContent:
        image, content = self._images[note_id][image_id]
        return ImageContent(metadata=image, content=content)

    async def list_images(self, note_id: UUID) -> list[ImageEntity]:
        return [image for image, _ in self._images.get(note_id, {}).values()]


class DbS3ImageStorage(ImageStorage):
    """Stores image bytes in S3 and metadata in DB."""

    def __init__(
        self, session: AsyncSession, s3_client: S3Client, settings: Settings
    ) -> None:
        self._session = session
        self._s3_client = s3_client
        if settings.s3_bucket_name is None:
            raise ValueError("No S3 Bucket name specified")
        self._bucket_name = settings.s3_bucket_name

    async def store_image(self, image: ImageEntity, content: bytes) -> ImageEntity:
        await asyncio.to_thread(
            self._s3_client.put_object,
            Bucket=self._bucket_name,
            Key=image.object_key,
            Body=content,
            ContentType=image.mime_type,
        )
        try:
            stored_image = await self._session.merge(image)
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            await asyncio.to_thread(
                self._s3_client.delete_object,
                Bucket=self._bucket_name,
                Key=image.object_key,
            )
            raise
        return stored_image

    async def get_image(self, note_id: UUID, image_id: UUID) -> ImageContent:
        statement = select(ImageEntity).where(
            ImageEntity.note_id == note_id,
            ImageEntity.id == image_id,
        )
        image = await self._session.scalar(statement)
        if image is None:
            raise KeyError((note_id, image_id))

        def read_object() -> bytes:
            response = self._s3_client.get_object(
                Bucket=self._bucket_name,
                Key=image.object_key,
            )
            body = response["Body"]
            try:
                return body.read()
            finally:
                body.close()

        content = await asyncio.to_thread(read_object)
        return ImageContent(metadata=image, content=content)

    async def list_images(self, note_id: UUID) -> list[ImageEntity]:
        statement = (
            select(ImageEntity)
            .where(ImageEntity.note_id == note_id)
            .order_by(ImageEntity.created_at, ImageEntity.id)
        )
        result = await self._session.scalars(statement)
        return list(result.all())

