from abc import ABC, abstractmethod

class LogicInterface(ABC):
    @abstractmethod
    def get(self, id: int) -> any:
        pass

class EntryTypeProvider(ABC):
    @abstractmethod
    def get_type(self, id: int) -> str:
        pass

class Deletable(ABC):
    @abstractmethod
    def delete(self, id: int):
        pass

class UserInterface(LogicInterface, Deletable):
    @abstractmethod
    def get_user(self, id):
        pass

    @abstractmethod
    def change_role(self, source_id, target_id, role):
        pass

    @abstractmethod
    def change_username(self, id, username):
        pass

    @abstractmethod
    def change_display_name(self, id, display_name):
        pass
    
    @abstractmethod
    def register_user(self, discord_id, display_name, username) -> int:
        pass

class RepealInterface(LogicInterface):
    @abstractmethod
    def get_repeal(self, entry_id):
        pass

    @abstractmethod
    def set_repeal(self, entry_id, repealed_id):
        pass

class EntryInterface(LogicInterface):
    @abstractmethod
    def get_entry(self, id):
        pass

    @abstractmethod
    def complete_entry(self, id, forced = False):
        pass

    @abstractmethod
    def cancel_entry(self, id):
        pass
    
    @abstractmethod
    def approve_entry(self, id):
        pass
    
    @abstractmethod
    def deny_entry(self, id):
        pass
    
    @abstractmethod
    def repeal_entry(self, id):
        pass
    
    @abstractmethod
    def register_entry(self, title, content, type, author, role, deadline) -> int:
        pass

class VotingInterface(LogicInterface):
    @abstractmethod
    def get_vote(self, voted_id: int):
        pass
    
    @abstractmethod
    def cast_vote(self, caster_id: int, voted_id: int, vote: str):
        pass

    @abstractmethod
    def is_voting_done(self, voted_id: int):
        pass

    @abstractmethod
    def get_verdict(self, voted_id: int):
        pass

class ElectionInterface(LogicInterface):
    @abstractmethod
    def get_election(self, election_id: int):
        pass

    @abstractmethod
    def elect(self, elector_id: int, elected_id: int):
        pass

    @abstractmethod
    def is_election_done(self, election_id: int):
        pass

    @abstractmethod
    def get_winner(self, election_id: int):
        pass