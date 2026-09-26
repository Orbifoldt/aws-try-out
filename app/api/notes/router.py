from uuid import UUID, uuid4

from fastapi import HTTPException

from app.api.notes.generated.main import NotesAPI
from app.api.notes.generated.models import Note, NoteCreate
from app.models.note import NoteEntity
from app.notes_storage import InMemoryNotesStorage, NotesStorage


class NotesAPIImpl(NotesAPI):
    def __init__(self) -> None:
        super().__init__()
        self._notes_storage: NotesStorage = InMemoryNotesStorage()

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

    async def create_note(self, body: NoteCreate) -> Note:
        note = self._to_entity(body)
        stored_note = await self._notes_storage.store_note(note)
        return self._from_entity(stored_note)

    async def list_notes(self) -> list[Note]:
        notes = await self._notes_storage.list_notes()
        return [self._from_entity(note) for note in notes]

    async def get_note(self, note_id: UUID) -> Note:
        try:
            note = await self._notes_storage.get_note(note_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Note not found") from None

        return self._from_entity(note)
