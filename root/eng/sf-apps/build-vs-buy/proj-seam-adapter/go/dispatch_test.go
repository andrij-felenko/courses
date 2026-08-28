// dispatch_test.go — ядро без мережі, підмінивши порт.
type fakeNotifier struct {
    calls   []domain.Event
    outcome error
}

func (f *fakeNotifier) Notify(to domain.Recipient, e domain.Event) error {
    f.calls = append(f.calls, e)
    return f.outcome
}

func TestRetryScheduledOnRetryable(t *testing.T) {
    fake := &fakeNotifier{outcome: fmt.Errorf("test: %w", domain.ErrRetryable)}
    d := domain.Dispatch{Notifier: fake}

    d.OnCourierAssigned(order, customer)

    if len(fake.calls) != 1 {
        t.Fatalf("очікували 1 виклик, отримали %d", len(fake.calls))
    }
    if _, ok := fake.calls[0].(domain.CourierNear); !ok {
        t.Errorf("очікували подію CourierNear")
    }
}
