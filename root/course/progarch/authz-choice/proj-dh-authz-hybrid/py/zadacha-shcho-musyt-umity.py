# ❌ Три тихі помилки в одному охайному на вигляд класі.
class NaiveHybrid:
    def __init__(self, policy, rels):
        self.policy, self.rels = policy, rels

    def can(self, user, action, resource) -> bool:          # (1) синхронний — ламає шов А
        try:
            is_member = self.rels.is_member_of_sync(user.id, resource.home_id)
        except Exception:
            is_member = True                                # (2) збій центру → «пустити»
        role = user.role_in_home.get(resource.home_id)
        return self.policy.evaluate(action=action, role=role,
                                    is_member=is_member, now=time.time() * 1000)
