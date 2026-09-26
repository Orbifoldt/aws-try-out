from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import NoteEntity


class NotesStorage(ABC):
    @abstractmethod
    async def store_note(self, note: NoteEntity) -> NoteEntity:
        ...
    
    @abstractmethod
    async def get_note(self, note_id: UUID) -> NoteEntity:
        ...

    @abstractmethod
    async def list_notes(self) -> list[NoteEntity]:
        ...


class InMemoryNotesStorage(NotesStorage):
    def __init__(self) -> None:
        self._notes: dict[UUID, NoteEntity] = {}

    async def store_note(self, note: NoteEntity) -> NoteEntity:
        """Store a note, replacing an existing note with the same ID."""
        self._notes[note.id] = note
        return note

    async def get_note(self, note_id: UUID) -> NoteEntity:
        """Return a note by ID, raising KeyError when it does not exist."""
        return self._notes[note_id]

    async def list_notes(self) -> list[NoteEntity]:
        """Return all notes in insertion order."""
        return list(self._notes.values())


class DbNotesStorage(NotesStorage):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def store_note(self, note: NoteEntity) -> NoteEntity:
        stored_note = await self._session.merge(note)
        await self._session.commit()
        return stored_note

    async def get_note(self, note_id: UUID) -> NoteEntity:
        note = await self._session.get(NoteEntity, note_id)
        if note is None:
            raise KeyError(note_id)
        return note

    async def list_notes(self) -> list[NoteEntity]:
        result = await self._session.scalars(select(NoteEntity))
        return list(result.all())
