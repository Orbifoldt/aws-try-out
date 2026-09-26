from dishka import AsyncContainer, Provider, Scope, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from app.database import DatabaseProvider
from app.notes_storage import DbNotesStorage, InMemoryNotesStorage, NotesStorage
from app.settings import Settings


def create_container(settings: Settings) -> AsyncContainer:
    """Choose the storage adapter once, with lifetimes owned by this container."""
    application = Provider()
    application.from_context(Settings, scope=Scope.APP)
    providers = [application, FastapiProvider()]

    if settings.use_in_memory_db:
        application.provide(
            InMemoryNotesStorage, provides=NotesStorage, scope=Scope.APP
        )
    else:
        application.provide(DbNotesStorage, provides=NotesStorage, scope=Scope.REQUEST)
        providers.append(DatabaseProvider())

    return make_async_container(*providers, context={Settings: settings})
