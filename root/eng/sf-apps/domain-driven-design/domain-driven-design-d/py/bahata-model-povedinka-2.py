# Багата модель: поліс сам стежить за своїми правилами
class Policy:
    def __init__(self):
        self._status = PolicyStatus.ACTIVE
        self._balance = 0

    # єдиний спосіб увійти в пільговий період — через це правило
    def enter_grace_period(self) -> None:
        if self._status is not PolicyStatus.ACTIVE:
            raise DomainError("до пільгового періоду входять лише з активного")
        if self._balance < 0:
            raise DomainError("не можна з простроченим внеском")
        self._status = PolicyStatus.GRACE_PERIOD

    def is_active(self) -> bool:
        return self._status is PolicyStatus.ACTIVE
