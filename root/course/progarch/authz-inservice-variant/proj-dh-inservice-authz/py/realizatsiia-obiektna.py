ACTIONS_BY_ROLE: dict[Role, frozenset[Action]] = {
    "owner":    frozenset({"unlock", "lock", "view", "configure"}),
    "resident": frozenset({"unlock", "lock", "view"}),
    "guest":    frozenset({"view"}),
}

class InServiceAuthorizer:
    def __init__(self, memberships: Memberships) -> None:
        self._memberships = memberships

    async def can(self, user: User, action: Action, resource: Resource) -> bool:
        # Ключ пошуку — дім САМОГО об'єкта. Тут і закривається IDOR.
        role = await self._memberships.role_in(user.id, resource.home_id)
        if role is None:
            return False                                        # не член ЦЬОГО дому → ні
        return action in ACTIONS_BY_ROLE.get(role, frozenset())  # відмова за замовчуванням
