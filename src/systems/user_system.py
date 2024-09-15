from dataclasses import dataclass

from exceptions import *
from database import Database
from utils.cache import Cache

def can_change_role(source_role, target_role):
    pass 

@dataclass
class User:
    id: int
    discord_id: int
    last_seen_username: str
    display_name: str
    role: str

class UserRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def get_user(self, id) -> User:
        pass

    def set_role(self, id, role):
        pass

    def update_username(self, id, username):
        pass

    def update_display_name(self, id, display_name):
        pass

    def create_user(self, discord_id, display_name, username, role = "everyone"):
        pass

    def delete_user(self, id):
        pass

class UserLogic:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository
        self._cache = Cache()

    def get_user(self, id) -> User:
        return self._cache.get(id, lambda: self._repository.get_user(id))
    
    def change_role(self, source_id, target_id, role):
        source_user = self.get_user(source_id)
        target_user = self.get_user(target_id)
        if not can_change_role(source_user.role, target_user.role):
            raise UserNotEnoughPermissionsError("Couldn't change role due to lack of permissions")
        self._repository.set_role(target_id, role)
        self._cache.clear_cache(target_id)

    def update_username(self, id, username):
        self.update_username(id, username)
        
    def update_display_name(self, id, display_name):
        self.update_display_name(id, display_name)

    def delete_user(self, id):
        self._repository.delete_user(id)
    
    def register_user(self, discord_id, display_name, username):
        self._repository.create_user(discord_id, display_name, username)