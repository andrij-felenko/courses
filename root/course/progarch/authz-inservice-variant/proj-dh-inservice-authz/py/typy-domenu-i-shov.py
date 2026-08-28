from typing import Literal, Optional, Protocol

Role   = Literal["owner", "resident", "guest"]
Action = Literal["unlock", "lock", "view", "configure"]

class User(Protocol):
    id: str

class Resource(Protocol):
    home_id: str                       # будь-що з приналежністю до дому: замок, камера…

class Authorizer(Protocol):            # ШОВ: обробники бачать ЛИШЕ це
    async def can(self, user: User, action: Action, resource: Resource) -> bool: ...

class Memberships(Protocol):           # ПОРТ до членства
    # Яка роль у користувача В ЦЬОМУ домі? Ключ — home_id, іншого способу спитати нема.
    async def role_in(self, user_id: str, home_id: str) -> Optional[Role]: ...
