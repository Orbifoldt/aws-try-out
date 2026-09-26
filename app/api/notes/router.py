from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.notes.generated.main import NotesAPI
from app.api.notes.generated.models import Note, NoteCreate
from app.database import NullSession, get_session
from app.models.note import NoteEntity
from app.notes_storage import DbNotesStorage, InMemoryNotesStorage, NotesStorage
from app.settings import get_settings


class NotesAPIImpl(NotesAPI):
    def __init__(self) -> None:
        super().__init__()
        self._in_memory_storage: NotesStorage = InMemoryNotesStorage()

    def _get_storage(self, session: AsyncSession | NullSession) -> NotesStorage:
        if isinstance(session, NullSession):
            return self._in_memory_storage
        return DbNotesStorage(session)

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
        session: Annotated[AsyncSession | NullSession, Depends(get_session)],
    ) -> Note:
        note = self._to_entity(body)
        stored_note = await self._get_storage(session).store_note(note)
        return self._from_entity(stored_note)

    async def list_notes(
        self,
        session: Annotated[AsyncSession | NullSession, Depends(get_session)],
    ) -> list[Note]:
        print(f"settings: {get_settings()}")
        notes = await self._get_storage(session).list_notes()
        return [self._from_entity(note) for note in notes]

    async def get_note(
        self,
        note_id: UUID,
        session: Annotated[AsyncSession | NullSession, Depends(get_session)],
    ) -> Note:
        try:
            note = await self._get_storage(session).get_note(note_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Note not found") from None

        return self._from_entity(note)
