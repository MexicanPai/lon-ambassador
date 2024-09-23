from systems.interface.abstract_logic import VotingInterface

class VoteProxy:
    def __init__(self, logic: VotingInterface, id) -> None:
        self._logic = logic
        self._id = id

    @property
    def info(self):
        return self._logic.get_vote(self._id)

    def cast_vote(self, caster_id: int, vote: str):
        self._logic.cast_vote(caster_id, self._id, vote)

    def is_voting_done(self):
        return self._logic.is_voting_done(self._id)
    
    def get_verdict(self):
        return self._logic.get_verdict(self._id)

    