from enum import Enum, auto


class PolicyStatus(Enum):
    DRAFT = auto()
    ACTIVE = auto()
    GRACE = auto()
    CANCELLED = auto()


class DomainError(Exception):
    """Порушення доменного правила поліса."""


class Policy:
    def __init__(self, policy_id, currency, due_date):
        self._id = policy_id
        self._currency = currency
        self._due_date = due_date
        self._status = PolicyStatus.DRAFT
        self._premium = 0
        self._payments = []

    # КОМАНДА: правило переходу тепер ТУТ, разом зі своїм вартовим
    def activate(self) -> None:
        if self._status is not PolicyStatus.DRAFT:
            raise DomainError("активувати можна лише чернетку")
        self._status = PolicyStatus.ACTIVE

    def enter_grace_period(self) -> None:
        if self._status is not PolicyStatus.ACTIVE:      # ← перевірка, якої бракувало
            raise DomainError("у пільговий період входять лише з активного")
        self._status = PolicyStatus.GRACE

    @property
    def status(self) -> PolicyStatus:
        return self._status
