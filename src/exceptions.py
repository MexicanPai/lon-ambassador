class AmbassadorError(Exception):
    """Base class for all Ambassador related exceptions."""
    pass

class AmbassadorInvalidStateError(AmbassadorError):
    """Raised when there was an invalid state"""

class AmbassadorLogicAlreadyRegisteredError(AmbassadorError):
    """Raised when there was an attempt to register a logic class to an already registered type"""

class AmbassadorOperationNotSupportedError(AmbassadorError):
    """Raised when an unsupported operation is attempted on a given entry"""
class EntryError(AmbassadorError):
    """Base class for all entry related exceptions."""
    pass

class EntryNotFoundError(EntryError):
    """Raised when an entry was not found in the database."""
    pass

class EntryDeadlineNotReachedError(EntryError):
    """Raised when an operation is attempted on an entry whose deadline has not been reached."""
    pass

class EntryCancelledError(EntryError):
    """Raised when an operation is attempted on a cancelled entry."""
    pass

class EntryAlreadyCompletedError(EntryError):
    """Raised when an operation is attempted on a completed entry"""

class EntryDeniedError(EntryError):
    """Raised when an operation is attempted on a denied entry"""

class EntryAlreadyApprovedError(EntryError):
    """Raised when an operation is attempted on an approved entry"""

class EntryNotActiveError(EntryError):
    """Raised when an operation is attempted on an entry which is not active"""

class UserError(AmbassadorError):
    """Base class for all user related exceptions."""

class UserNotFoundError(AmbassadorError):
    """Raised when a user is not found in the database"""

class UserNotEnoughPermissionsError(UserError):
    """Raised when an operation is attempted without enough permissions"""

class VoteError(AmbassadorError):
    """Base class for all vote related exceptions."""

class VoteNotDoneError(VoteError):
    """Raised when an operation is attempted on a vote that was not completed"""

class VoteAlreadyDoneError(VoteError):
    """Raised when an operation is attempted on a vote which was already completed"""