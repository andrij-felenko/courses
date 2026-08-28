// tests/dispatch.test.ts — ядро перевіряємо БЕЗ мережі, підмінивши порт.
class FakeNotifier implements Notifier {
  public calls: { to: Recipient; event: DomainEvent }[] = [];
  constructor(private outcome: NotifyOutcome = { status: "delivered" }) {}
  async notify(to: Recipient, event: DomainEvent): Promise<NotifyOutcome> {
    this.calls.push({ to, event });
    return this.outcome;
  }
}

test("на retryable ядро призначає повтор", async () => {
  const fake = new FakeNotifier({ status: "retryable", reason: "test" });
  const dispatch = new OrderDispatch(fake);

  await dispatch.onCourierAssigned(order, customer);

  expect(fake.calls).toHaveLength(1);
  expect(fake.calls[0].event.kind).toBe("courier_near");
  expect(dispatch.pendingRetries).toContain(order.id);
});
