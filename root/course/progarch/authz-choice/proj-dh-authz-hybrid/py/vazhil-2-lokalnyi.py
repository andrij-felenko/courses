class HybridAuthorizer:
    def __init__(self, policies, rels, now=lambda: time.time() * 1000):
        self._policies = policies    # PolicySource: .policy() -> Policy (без I/O)
        self._rels = rels            # RelationshipCache
        self._now = now

    async def can(self, user, action, resource) -> bool:
        try:
            policy = self._policies.policy()      # читання вказівника — без I/O
        except Exception:
            return False                          # правила ще нема (старт/збій) → deny
        is_member = await self._rels.is_member_of(user.id, resource.home_id)  # кеш; fail-closed
        role = user.role_in_home.get(resource.home_id)                        # локальний факт
        # ВЕРДИКТ — у процесі, за центральним правилом. Жодного стрибка на рішення.
        return policy.evaluate(action=action, role=role, is_member=is_member, now=self._now())
