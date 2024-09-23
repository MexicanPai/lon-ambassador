from typing import NamedTuple

from dataclasses import dataclass
from exceptions import *
from database import Database
from systems.interface.abstract_logic import UserInterface
from utils.cache import Cache

def can_change_role(source_role, target_role):
    pass 

class User(NamedTuple):
    id: int
    discord_id: int
    username: str
    display_name: str
    role: str

class UserRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def get_user(self, id) -> User:
        entry = self._db.query_once("""SELECT a.id, a.discord_id, a.discord_username, a.display_name, b.role
                       FROM user a
                       JOIN roles b ON a.role = b.id
                       WHERE a.id = ?
                       """, id)
        return User(*entry)

    def set_role(self, id, role):
        self._db.execute("UPDATE user SET role = (SELECT id FROM roles WHERE role = ?) WHERE id = ?", role, id)
        self._db.commit()

    def update_username(self, id, username):
        self._db.execute("UPDATE user SET discord_username = ? WHERE id = ?", username, id)
        self._db.commit()

    def update_display_name(self, id, display_name):
        self._db.execute("UPDATE user SET display_name = ? WHERE id = ?", display_name, id)
        self._db.commit()

    def create_user(self, discord_id, display_name, username, role = "everyone"):
        result = self._db.execute("""INSERT INTO user (discord_id, discord_username, display_name, role) VALUES(
                         ?, ?, ?,
                         (SELECT id FROM roles WHERE role = ?)
                         )
                         """, discord_id, username, display_name, role)
        self._db.commit()
        return result.lastrowid

    def delete_user(self, id):
        pass

class UserLogic(UserInterface):
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository
        self._cache = Cache()

    def get(self, id) -> User:
        return self._cache.get(id, lambda: self._repository.get_user(id))
    
    def get_user(self, id):
        return self.get(id)
    
    def change_role(self, source_id, target_id, role):
        source_user = self.get(source_id)
        target_user = self.get(target_id)
        if not can_change_role(source_user.role, target_user.role):
            raise UserNotEnoughPermissionsError("Couldn't change role due to lack of permissions")
        self._repository.set_role(target_id, role)
        self._cache.clear_cache(target_id)

    def change_username(self, id, username):
        self._repository.update_username(id, username)
        
    def change_display_name(self, id, display_name):
        self._repository.update_display_name(id, display_name)

    def delete(self, id):
        self._repository.delete_user(id)
    
    def register_user(self, discord_id, display_name, username) -> int:
        return self._repository.create_user(discord_id, display_name, username)