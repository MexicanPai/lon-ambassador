from typing import Literal, NamedTuple

from exceptions import *
from database import Database
from utils.cache import Cache
from systems.interface.abstract_logic import VotingInterface, EntryInterface, UserInterface
from systems.entry_system import Entry

class Vote(NamedTuple):
    entry_id: int
    votes: dict[int, str]

    def get_current_verdict(self):
        approve_count = 0
        deny_count = 0
        for vote in self.votes.values():
            if vote == "approve":
                approve_count += 1
            elif vote == "disapprove":
                deny_count += 1
        if approve_count == deny_count:
            return "tie"
        elif approve_count > deny_count:
            return "approved"
        return "denied"
    
class VoteRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def get_vote(self, id) -> Vote:
        result = self._db.query("SELECT caster, vote FROM vote_store WHERE entry = ?", id)
        vote_dict = {}
        for caster, vote in result:
            vote_dict[caster] = vote
        return Vote(id, vote_dict)

    def cast_vote(self, entry_id: int, user_id: str, vote):
        self._db.insert("vote_store", {"caster": user_id, "entry": entry_id, "vote": vote})
        self._db.commit()

class VoteLogic(VotingInterface):
    def __init__(self, repository: VoteRepository, user_logic: UserInterface, entry_logic: EntryInterface) -> None:
        self._repository = repository
        self._user_logic = user_logic
        self._entry_logic = entry_logic
        self._cache = Cache()

    def get(self, id):
        return self.get_vote(id)

    def get_vote(self, id) -> Vote:
        return self._cache.get(id, lambda: self._repository.get_vote(id))
    
    def cast_vote(self, caster_id: str, entry_id: int, vote: Literal["approve", "disapprove", "abstain"]):
        entry: Entry = self._entry_logic.get_entry(entry_id)
        if entry.is_completed():
            raise VoteAlreadyDoneError("Couldn't cast vote. The vote was already completed")
        if entry.is_cancelled():
            raise VoteAlreadyDoneError("Couldn't cast vote. The vote was already cancelled")
        if not entry.is_active():
            raise VoteAlreadyDoneError("Couldn't cast vote. The vote is not active")
        
        caster = self._user_logic.get_user(caster_id)
        if not entry.has_user_permissions(caster.role):
            raise UserNotEnoughPermissionsError("Couldn't cast vote. The user does not have enough permissions")

        self._repository.cast_vote(entry_id, caster_id, vote)
        self._cache.clear_cache(caster_id)

    def is_voting_done(self, voted_id: int):
        pass

    def get_verdict(self, entry_id):
        entry: Entry = self._entry_logic.get_entry(entry_id)
        if entry.is_active():
            raise VoteNotDoneError("Couldn't get verdict. The vote was not completed")
        if entry.is_cancelled():
            raise EntryCancelledError("Couldn't get verdict. The vote was cancelled")
        if not entry.is_completed():
            raise VoteNotDoneError("Couldn't get verdict. There is no vote happening") # aa i want to use a differenttt thingy for this
        vote = self._repository.get_vote(entry_id)
        return vote.get_current_verdict()