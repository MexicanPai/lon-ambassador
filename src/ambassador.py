from database import Database

class Ambassador:
    def __init__(self, db: Database) -> None:
        self.db = db

    def register_entry(self, entry):
        pass

    def get_entry(self, entry_id: int):
        pass

    def get_entry_by_name(self, entry_name: str):
        pass

    def cast_approved_vote(self, caster, entry):
        pass

    def cast_denied_vote(self, caster, entry):
        pass

    def elect_person(self, elector, elected, entry):
        pass