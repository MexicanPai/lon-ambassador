from systems.interface.abstract_logic import EntryInterface

class EntryProxy:
    def __init__(self, logic: EntryInterface, id) -> None:
        self._logic = logic
        self._id = id

    @property
    def info(self):
        return self._logic.get_entry(self._id)

    def approve(self):
        self._logic.approve_entry(self._id)

    def deny(self):
        self._logic.deny_entry(self._id)

    def cancel(self):
        self._logic.cancel_entry(self._id)

    def complete(self, *, early=False):
        self._logic.complete_entry(self._id, early)

    