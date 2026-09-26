from abc import ABC, abstractmethod
from uuid import UUID

from app.models.note import NoteEntity


class NotesStorage(ABC):
    @abstractmethod
    async def store_note(self, note: NoteEntity) -> NoteEntity:
        ...
    
    @abstractmethod
    async def get_note(self, id: UUID) -> NoteEntity:
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

    async def get_note(self, id: UUID) -> NoteEntity:
        """Return a note by ID, raising KeyError when it does not exist."""
        return self._notes[id]

    async def list_notes(self) -> list[NoteEntity]:
        """Return all notes in insertion order."""
        return list(self._notes.values())
