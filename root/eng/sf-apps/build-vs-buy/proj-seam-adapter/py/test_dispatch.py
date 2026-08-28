# tests/test_dispatch.py — ядро без мережі, підмінивши порт.
class FakeNotifier:                          # реалізує Notifier структурно
    def __init__(self, outcome: NotifyOutcome = NotifyOutcome.delivered()) -> None:
        self.calls: list[tuple[Recipient, DomainEvent]] = []
        self._outcome = outcome
    def notify(self, to: Recipient, event: DomainEvent) -> NotifyOutcome:
        self.calls.append((to, event))
        return self._outcome

def test_retry_scheduled_on_retryable():
    fake = FakeNotifier(NotifyOutcome.retryable("test"))
    dispatch = OrderDispatch(fake)

    dispatch.on_courier_assigned(order, customer)

    assert len(fake.calls) == 1
    assert isinstance(fake.calls[0][1], CourierNear)
    assert order.id in dispatch.pending_retries
