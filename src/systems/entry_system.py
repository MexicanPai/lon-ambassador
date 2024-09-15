from dataclasses import dataclass
import time

from exceptions import *
from database import Database
from utils.cache import Cache

@dataclass
class Entry:
    id: int
    type: str
    state: str
    author: str
    creation_date: int
    end_date: int
    role: int

    def is_past_due(self, time: int):
        return time > self.end_date
    
    def is_active(self):
        return self.state == "active"
    def is_cancelled(self):
        return self.state == "cancelled"
    def is_completed(self):
        return self.state in ("completed", "completed_early", "repealed")
    
    def is_approved(self):
        return self.is_completed() or self.is_cancelled() or self.is_active()
    def is_denied(self):
        return self.state == "denied"
    def is_proposed(self):
        return self.state == "proposed"
    
    def has_user_permissions(self, user_role):
        return self.role <= user_role
    def is_author(self, user):
        return user == self.author

class EntryRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def get_entry(self, id) -> Entry:
        pass

    def mark_as_completed(self, id, early = False):
        pass

    def mark_as_cancelled(self, id):
        pass

    def mark_as_active(self, id):
        pass

    def mark_as_denied(self, id):
        pass

    def create_entry(self, type, author, role, end_date, creation_date = time.time(), state = "proposed"):
        pass

class EntryLogic:
    def __init__(self, repository: EntryRepository) -> None:
        self._repository = repository
        self._cache = Cache()

    def get_entry(self, id) -> Entry:
        return self._cache.get(id, lambda: self._repository.get_entry(id))
    
    def complete_entry(self, id, forced = False):
        entry = self.get_entry(id)

        if entry.is_completed():
            return False
        if entry.is_cancelled():
            raise EntryCancelledError("This entry was already cancelled and cannot be completed!")
        
        if not entry.is_past_due(time.time()):
            if not forced:
                raise EntryDeadlineNotReachedError("This entry did not reach its deadline yet")
            self._repository.mark_as_completed(id, early=True)
        else:
            self._repository.mark_as_completed(id, early=False)
        
        self._cache.clear_cache(id)
        return True

    def cancel_entry(self, id):
        entry = self.get_entry(id)

        if entry.is_cancelled():
            return False
        if entry.is_completed():
            raise EntryAlreadyCompletedError("This entry was already completed and cannot be cancelled")
        
        self._repository.mark_as_cancelled(id)
        self._cache.clear_cache(id)
        return True

    def approve_entry(self, id):
        entry = self.get_entry(id)

        if entry.is_approved():
            raise False
        if entry.is_denied():
            raise EntryDeniedError("This entry was already denied and cannot be approved")
        
        self._repository.mark_as_active(id)
        self._cache.clear_cache(id)
        return True
    
    def deny_entry(self, id):
        entry = self.get_entry(id)

        if entry.is_denied():
            return False
        if entry.is_approved():
            raise EntryAlreadyApprovedError("This entry was already approved and cannot be denied")
        
        self._repository.mark_as_cancelled(id)
        self._cache.clear_cache(id)
        return True
    
    def register_entry(self, type, author, role, deadline):
        self._repository.create_entry(type, author, role, end_date=deadline)
