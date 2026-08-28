from dataclasses import dataclass
from typing import Protocol, Optional

# контракт — простий носій даних, без жодної поведінки
@dataclass
class UserRow:
    id: int
    email: str
    role: str
    active: bool

# інтерфейс DAO — що з цими даними можна робити
class UserDao(Protocol):
    def find_by_id(self, id: int) -> Optional[UserRow]: ...
    def find_by_role(self, role: str) -> list[UserRow]: ...
    def insert(self, u: UserRow) -> None: ...
    def update(self, u: UserRow) -> None: ...
    def delete(self, id: int) -> None: ...

# бізнес-код залежить ЛИШЕ від інтерфейсу — жодного натяку на сховище
class ApprovalService:
    def __init__(self, users: UserDao):
        self._users = users

    def approver_emails(self) -> list[str]:
        rows = self._users.find_by_role("approver")
        return [u.email for u in rows if u.active]
