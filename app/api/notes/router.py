from uuid import UUID, uuid4

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException

from app.api.notes.generated.main import register_notes_routes
from app.api.notes.generated.models import Note, NoteCreate
from app.models.note import NoteEntity
from app.notes_storage import NotesStorage


class NotesAPIImpl:
    def __init__(self) -> None:
        self.router = APIRouter(route_class=DishkaRoute)
        register_notes_routes(
            self.router,
            create_note=self.create_note,
            list_notes=self.list_notes,
            get_note=self.get_note,
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
