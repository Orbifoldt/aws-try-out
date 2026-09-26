from dataclasses import dataclass
from uuid import UUID


@dataclass
class NoteEntity:
    id: UUID
    title: str
    body: str