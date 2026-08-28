from typing import Literal, Optional, Protocol, Mapping

Role   = Literal["owner", "resident", "guest"]
Action = Literal["unlock", "lock", "view", "configure"]

class User(Protocol):
    id: str
    role_in_home: Mapping[str, Optional[Role]]   # роль їде з токеном (локальний факт)

class Resource(Protocol):
    home_id: str

class Authorizer(Protocol):                      # ШОВ — той самий, що у Варіанті А
    async def can(self, user: User, action: Action, resource: Resource) -> bool: ...
