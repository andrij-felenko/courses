from dataclasses import dataclass


@dataclass(frozen=True)
class ArchFinding:
    scenario: str           # сценарій із мірою, що народив знахідку
    finding: str            # чим саме структура може не витягти (одним реченням)
    kind: FindingKind       # ризик / неризик / чутливість / компроміс
    owner: str | None       # хто відповідає за зняття; None == нічий == мертвий
    state: FindingState     # де знахідка зараз
    due_day: int = 0        # дедлайн зняття, день від старту проєкту (0 == не призначено)
