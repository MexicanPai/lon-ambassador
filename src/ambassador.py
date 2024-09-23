from database import Database
from systems.interface.abstract_logic import *
from exceptions import *
from proxies.user_proxy import UserProxy
from proxies.vote_proxy import VoteProxy
from proxies.entry_proxy import EntryProxy

class Ambassador:
    def __init__(self, type_provider: EntryTypeProvider, entry_logic: EntryInterface, user_logic: UserInterface) -> None:
        self._type_provider = type_provider
        self._logic_registry = {}
        self._entry_logic = entry_logic
        self._user_logic = user_logic
        
    def _get_type(self, id):
        return self._type_provider.get_type(id)
    
    def _get_logic_instance(self, type: str):
        return self._logic_registry.get(type, None)
    
    def _get_logic(self, entry_id: int, interface):
        type = self._get_type(entry_id)
        logic: interface = self._get_logic_instance(type)
        if not isinstance(logic, interface):
            raise AmbassadorOperationNotSupportedError(f"The entry of type \"{entry_id}\" does not support the attempted operation")
        return logic
    
    def register_logic(self, logic: LogicInterface, type: str):
        if type in self._logic_registry:
            raise AmbassadorLogicAlreadyRegisteredError(f"A logic instance was already registered for type \"{type}\"")
        self._logic_registry[type] = logic

    def register_entry(self, title, content, type, author, role, deadline) -> int:
        return self._entry_logic.register_entry(title, content, type, author, role, deadline)
    
    def register_user(self, discord_id, username, display_name):
        return self._user_logic.register_user(discord_id, display_name, username)

    def register_resolution(self, title, content, author, role, deadline):
        return self.register_entry(title, content, "resolution", author, role, deadline)

    def register_repeal(self, title, content, author, role, deadline, repealed_id):
        logic = self._get_logic_instance("repeal")
        entry_id = self.register_entry(title, content, "repeal", author, role, deadline)
        logic.set_repeal(entry_id, repealed_id)
        return entry_id
    
    def register_election(self, title, content, author, role, deadline, candidates: list[int]):
        pass
    
    def get_user_proxy(self, user_id):
        return UserProxy(self._user_logic, user_id)

    def get_vote_proxy(self, entry_id):
        logic = self._get_logic(entry_id, VotingInterface)
        return VoteProxy(logic, entry_id)
    
    def get_entry_proxy(self, entry_id):
        return EntryProxy(self._entry_logic, entry_id)
    
    def get_repeal_target(self, entry_id):
        logic = self._get_logic(entry_id, LogicInterface)
        return logic.get(entry_id)
    
    def get_election_proxy(self, entry_id):
        pass