HOUR = 3_600_000  # мс

class PolicyBundle:
    def __init__(self, version, actions_by_role, guest_unlock):
        self.version = version                 # ревізія (для 304 і аудиту)
        self.actions_by_role = actions_by_role # {role: [actions]}
        self.guest_unlock = guest_unlock        # (from_hour, to_hour)

class Policy:
    def __init__(self, version, table, guest):
        self.version, self._table, self._guest = version, table, guest

    def evaluate(self, action, role, is_member, now):
        if not is_member:                              # «член дому» — обов'язково (у центрі!)
            return False
        if role is None:                               # нема ролі в цьому домі → ні
            return False
        if action in self._table.get(role, frozenset()):
            return True                                # базовий дозвіл ролі
        if role == "guest" and action == "unlock":     # спец-правило гостя: денне вікно
            h = int((now / HOUR) % 24)
            return self._guest[0] <= h < self._guest[1]
        return False                                   # усе, чого не виписано, — заборонено

def compile_policy(b: PolicyBundle) -> Policy:
    table = {r: frozenset(a) for r, a in b.actions_by_role.items()}
    return Policy(b.version, table, b.guest_unlock)
