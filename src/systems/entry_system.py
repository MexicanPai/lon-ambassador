from typing import NamedTuple
import time

from exceptions import *
from database import Database
from systems.interface.abstract_logic import EntryInterface, EntryTypeProvider
from utils.cache import Cache

class Entry(NamedTuple):
    id: int
    type: str
    state: str
    role: int
    author: str
    creation_date: int
    end_date: int
    title: str
    content: str

    def is_past_due(self, current_time = None):
        current_time = current_time or time.time()
        return current_time > self.end_date
    
    def is_active(self):
        return self.state == "active"
    def is_cancelled(self):
        return self.state == "cancelled"
    def is_completed(self):
        return self.state in ("completed", "completed early", "repealed")
    
    def is_approved(self):
        return self.is_completed() or self.is_cancelled() or self.is_active()
    def is_denied(self):
        return self.state == "denied"
    def is_proposed(self):
        return self.state == "proposed"
    
    def has_user_permissions(self, user_role):
        return True #self.role <= user_role
    
    def is_author(self, user):
        return user == self.author

class EntryRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def _mark_state(self, id, state):
        self._db.execute("""UPDATE entry_data
                        SET state = (SELECT id FROM state_types WHERE state = ?)
                        WHERE id = ?
            """, state, id)
        self._db.commit()

    def get_entry(self, id) -> Entry:
        entry = self._db.query_once("""SELECT a.id, b.type, c.state, a.role, a.author, a.creation_date, a.deadline, a.title, a.content
                       FROM entry_data a
                       JOIN entry_types b ON a.type = b.id
                       JOIN state_types c ON a.state = c.id
                       WHERE a.id = ?
                       """, id)
        return Entry(*entry)

    def mark_as_completed(self, id, early = False):
        if early:
            self._mark_state(id, "completed early")
        else:
            self._mark_state(id, "completed")

    def mark_as_cancelled(self, id):
        self._mark_state(id, "cancelled")

    def mark_as_active(self, id):
        self._mark_state(id, "active")

    def mark_as_denied(self, id):
        self._mark_state(id, "denied")

    def mark_as_repealed(self, id):
        self._mark_state(id, "repealed")

    def create_entry(self, title, content,type, author, role, end_date, creation_date = None, state = "proposed"):
        creation_date = creation_date or time.time()
        result = self._db.execute("""INSERT INTO entry_data (
                                  type, state, role, author, creation_date, deadline, title, content) 
                                  VALUES(
                                  (SELECT id FROM entry_types WHERE type = ?),
                                  (SELECT id FROM state_types WHERE state = ?),
                                  (SELECT id FROM roles WHERE role = ?),
                                  ?, ?, ?, ?, ?
                                  )
                                  """, type, state, role, author, creation_date, end_date, title, content)
        self._db.commit()
        return result.lastrowid

class EntryLogic(EntryInterface, EntryTypeProvider):
    def __init__(self, repository: EntryRepository) -> None:
        self._repository = repository
        self._cache = Cache()

    def get(self, id) -> Entry:
        return self._cache.get(id, lambda: self._repository.get_entry(id))
    
    def get_entry(self, id):
        return self.get(id)
    
    def get_type(self, id):
        return self.get(id).type
    
    def complete_entry(self, id, forced = False):
        entry = self.get(id)

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
        entry = self.get(id)

        if entry.is_cancelled():
            return False
        if entry.is_completed():
            raise EntryAlreadyCompletedError("This entry was already completed and cannot be cancelled")
        
        self._repository.mark_as_cancelled(id)
        self._cache.clear_cache(id)
        return True

    def approve_entry(self, id):
        entry = self.get(id)

        if entry.is_approved():
            raise False
        if entry.is_denied():
            raise EntryDeniedError("This entry was already denied and cannot be approved")
        
        self._repository.mark_as_active(id)
        self._cache.clear_cache(id)
        return True
    
    def deny_entry(self, id):
        entry = self.get(id)

        if entry.is_denied():
            return False
        if entry.is_approved():
            raise EntryAlreadyApprovedError("This entry was already approved and cannot be denied")
        
        self._repository.mark_as_cancelled(id)
        self._cache.clear_cache(id)
        return True
    
    def repeal_entry(self, id):
        entry: Entry = self.get(id)
        if entry.state == "repealed":
            return False
        if not entry.is_completed():
            raise AmbassadorInvalidStateError(f"An entry with state \"{entry.state}\" cannot be repealed")
        
        self._repository.mark_as_repealed(id)
        self._cache.clear_cache(id)
        return True
    
    def register_entry(self, title, content, type, author, role, deadline):
        return self._repository.create_entry(title, content, type, author, role, deadline)
