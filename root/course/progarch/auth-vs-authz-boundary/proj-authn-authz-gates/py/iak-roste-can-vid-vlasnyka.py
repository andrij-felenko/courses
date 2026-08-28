# роль → дозволені дії (гість лише читає, сім'я керує, засновник — усе)
GRANTS: dict[Role, set[Action]] = {
    "guest":   {"read"},
    "family":  {"read", "write"},
    "founder": {"read", "write", "manage"},
}

def can(subject: Subject, action: Action, home: Home) -> bool:
    role = memberships.role_of(subject.id, home.id)   # Role | None
    if role is None:
        return False                                  # не член → відмова
    return action in GRANTS[role]
