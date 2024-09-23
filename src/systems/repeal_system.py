from typing import NamedTuple

from exceptions import *
from database import Database
from utils.cache import Cache
from systems.interface.abstract_logic import VotingInterface, EntryInterface, RepealInterface
from systems.entry_system import Entry

class Repeal(NamedTuple):
    entry_id: int
    repealed_id: int
    
class RepealRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def get_repeal(self, id) -> Repeal:
        result = self._db.query_once("SELECT * FROM repeal_store WHERE entry_id = ?", id)
        return Repeal(*result)

    def set_repeal(self, id, repealed_id):
        self._db.insert("repeal_store", {"entry_id": id, "repealed_id": repealed_id})

class RepealLogic(RepealInterface, VotingInterface):
    def __init__(self, repository: RepealRepository, vote_logic: VotingInterface, entry_logic: EntryInterface) -> None:
        self._repository = repository
        self._vote_logic = vote_logic
        self._entry_logic = entry_logic
        self._cache = Cache()

    def get(self, id) -> Repeal:
        return self._cache.get(id, lambda: self._repository.get_repeal(id))
    
    def get_repeal(self, entry_id):
        return self.get(entry_id)

    def set_repeal(self, entry_id, repealed_id):
        entry: Entry = self._entry_logic.get(entry_id)
        if entry.type != "repeal":
            raise AmbassadorOperationNotSupportedError(f"Cannot set repeal to entry of type \"{entry.type}\"")
        self._repository.set_repeal(entry_id, repealed_id)
    
    def get_vote(self, id):
        return self._vote_logic.get_vote(id)
    
    def cast_vote(self, caster_id, entry_id, vote):
        self._vote_logic.cast_vote(caster_id, entry_id, vote)

    def is_voting_done(self, voted_id: int):
        return self._vote_logic.is_voting_done(voted_id)

    def get_verdict(self, entry_id):
        verdict = self._vote_logic.get_verdict(entry_id)
        if verdict == "denied":
            return verdict
        repeal_id = self.get(entry_id).repealed_id
        self._entry_logic.repeal_entry(repeal_id)
        return verdict