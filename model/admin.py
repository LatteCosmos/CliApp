"""
Admin domain object.

The brief states admins are existing university staff and do not have
to register, so the Admin class is mostly a marker type that inherits
the password slot from User to keep the inheritance hierarchy tidy.

The actual admin operations (list, group, partition, remove, clear)
live on AdminSystem so that the Admin class itself stays a pure model.
"""

from model.user import User


class Admin(User):
    """A university staff member with management privileges."""

    # The brief does not require admin authentication, so we use a
    # default placeholder password.  It is here purely so the User
    # superclass contract is honoured.
    def __init__(self, username: str = "admin", password: str = "admin"):
        super().__init__(password)
        self._username = username

    @property
    def username(self) -> str:
        return self._username
