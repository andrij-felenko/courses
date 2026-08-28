import asyncio
from dataclasses import dataclass

@dataclass
class U:    id: str
@dataclass
class Door: home_id: str

class StaticMemberships:                    # фейкове членство: user → home → role
    def __init__(self, table): self._table = table
    async def role_in(self, user_id, home_id):
        return self._table.get(user_id, {}).get(home_id)   # немає запису → None → «не член»

def test_foreign_resident_denied():
    async def scenario():
        authz = InServiceAuthorizer(StaticMemberships({
            "oksana": {"home-12": "resident"},   # Оксана — мешканка дому 12
            "bohdan": {"home-7":  "resident"},   # Богдан — мешканець дому 7
        }))
        door42 = Door("home-7")                  # замок Богдана

        # ГОЛОВНИЙ ДОКАЗ: чужий мешканець на чужому замку — DENY.
        assert await authz.can(U("oksana"),  "unlock",   door42) is False
        # Контроль: свій мешканець свій замок — можна.
        assert await authz.can(U("bohdan"),  "unlock",   door42) is True
        # Відмова за замовчуванням: невідома дія — ні.
        assert await authz.can(U("bohdan"),  "detonate", door42) is False
        # Відмова за замовчуванням: не член жодного дому — ні.
        assert await authz.can(U("stranger"), "unlock",  door42) is False

    asyncio.run(scenario())
