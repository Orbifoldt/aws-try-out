from datetime import UTC, datetime
from pathlib import PurePosixPath
from uuid import UUID, uuid4

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.api.notes.generated.main import register_routes
from app.api.notes.generated.models import Note, NoteCreate, NoteImage
from app.image_storage import ImageContent, ImageStorage
from app.models.image_entity import ImageEntity, ImageMimeType
from app.models.note import NoteEntity
from app.notes_storage import NotesStorage

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
IMAGE_SIGNATURES = {
    "image/jpeg": lambda content: content.startswith(b"\xff\xd8\xff"),
    "image/png": lambda content: content.startswith(b"\x89PNG\r\n\x1a\n"),
    "image/webp": lambda content: (
        len(content) >= 12
        and content.startswith(b"RIFF")
        and content[8:12] == b"WEBP"
    ),
}


class NotesAPIImpl:
    def __init__(self) -> None:
        self.router = APIRouter(route_class=DishkaRoute)
        register_routes(
            self.router,
            create_note=self.create_note,
            list_notes=self.list_notes,
            get_note=self.get_note,
            upload_note_image=self.upload_note_image,
            list_note_images=self.list_note_images,
            get_note_image=self.get_note_image,
        )

    @staticmethod
    def _to_entity(note_create: NoteCreate) -> NoteEntity:
        return NoteEntity(
            id=uuid4(),
            title=note_create.title,
            body=note_create.body,
        )

    @staticmethod
    def _from_entity(note_entity: NoteEntity) -> Note:
        return Note(
            id=note_entity.id,
            title=note_entity.title,
            body=note_entity.body,
        )

    async def create_note(
        self,
        body: NoteCreate,
        storage: FromDishka[NotesStorage],
    ) -> Note:
        note = self._to_entity(body)
        stored_note = await storage.store_note(note)
        return self._from_entity(stored_note)

    async def list_notes(
        self,
        storage: FromDishka[NotesStorage],
    ) -> list[Note]:
        notes = await storage.list_notes()
        return [self._from_entity(note) for note in notes]

    async def get_note(
        self,
        note_id: UUID,
        storage: FromDishka[NotesStorage],
    ) -> Note:
        try:
            note = await storage.get_note(note_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Note not found") from None

        return self._from_entity(note)

    @staticmethod
    async def _require_note(note_id: UUID, storage: NotesStorage) -> None:
        try:
            await storage.get_note(note_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Note not found") from None

    @staticmethod
    def _to_note_image(image: ImageEntity) -> NoteImage:
        return NoteImage(
            id=image.id,
            name=image.name,
            mime_type=image.mime_type.value,
            alt_text=image.alt_text,
            size_bytes=image.size_bytes,
            created_at=image.created_at,
        )

    async def upload_note_image(
        self,
        note_id: UUID,
        image_storage: FromDishka[ImageStorage],
        notes_storage: FromDishka[NotesStorage],
        image: UploadFile,  # TODO: can we remove the default value?
        alt_text: str | None = Form(default=None, max_length=500),
    ) -> NoteImage:
        await self._require_note(note_id, notes_storage)

        # Validate content type supported
        mime_type = image.content_type
        if mime_type is None or mime_type not in IMAGE_SIGNATURES:
            raise HTTPException(status_code=415, detail="Unsupported file type")

        # Validate content
        content = await image.read(MAX_IMAGE_SIZE_BYTES + 1)
        if len(content) > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="File is too large")
        if not content or not IMAGE_SIGNATURES[mime_type](content):
            raise HTTPException(status_code=415, detail="The uploaded bytes do not match the declared file type")

        # Validate filename
        raw_name = (image.filename or "image").replace("\\", "/")
        name = PurePosixPath(raw_name).name
        if not name or len(name) > 255:
            raise HTTPException(status_code=422, detail="Invalid image filename")

        image_id = uuid4()
        image_entity = ImageEntity(
            id=image_id,
            note_id=note_id,
            name=name,
            mime_type=ImageMimeType(mime_type),
            alt_text=alt_text,
            object_key=f"notes/{note_id}/images/{image_id}",
            size_bytes=len(content),
            created_at=datetime.now(UTC),
        )
        stored_image = await image_storage.store_image(image_entity, content)
        return self._to_note_image(stored_image)

    async def list_note_images(
        self,
        note_id: UUID,
        image_storage: FromDishka[ImageStorage],
        notes_storage: FromDishka[NotesStorage],
    ) -> list[NoteImage]:
        await self._require_note(note_id, notes_storage)
        images = await image_storage.list_images(note_id)
        return [self._to_note_image(image) for image in images]

    async def get_note_image(
        self,
        note_id: UUID,
        image_id: UUID,
        image_storage: FromDishka[ImageStorage],
    ) -> Response:
        try:
            image_content: ImageContent = await image_storage.get_image(
                note_id, image_id
            )
        except KeyError:
            raise HTTPException(
                status_code=404, detail="Note or image not found"
            ) from None

        return Response(
            content=image_content.content,
            media_type=image_content.metadata.mime_type.value,
        )
