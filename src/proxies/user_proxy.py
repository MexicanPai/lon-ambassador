from systems.interface.abstract_logic import UserInterface

class UserProxy:
    def __init__(self, logic: UserInterface, id) -> None:
        self._logic = logic
        self._id = id

    @property
    def info(self):
        return self._logic.get_user(self._id)

    def change_role(self, source_id, target_id, role):
        self._logic.change_role(source_id, target_id, role)

    def change_username(self, id, username):
        self._logic.change_username(id, username)

    def change_display_name(self, id, display_name):
        self._logic.change_display_name(id, display_name)

    