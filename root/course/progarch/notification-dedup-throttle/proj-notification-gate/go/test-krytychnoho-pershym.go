var t0 = time.Date(2026, 7, 11, 3, 0, 0, 0, time.UTC)

func TestCriticalBypassesEverything(t *testing.T) {
	st := newMemStore(func() time.Time { return t0 })
	var sent []Notification
	g := newGate(st, func(_ context.Context, out Notification) error {
		sent = append(sent, out)
		return nil
	})

	fire := Notification{Recipient: "petrenko", Event: "smoke@03:00",
		Class: "safety", Channel: "push", Severity: Critical}

	_, _ = g.Admit(context.Background(), fire)
	_, _ = g.Admit(context.Background(), fire) // та сама подія ВДРУГЕ — критичне не дедупимо

	if len(sent) != 2 {
		t.Fatalf("критичне мусить доставитись обидва рази (в обхід дедупу), а пішло %d", len(sent))
	}
}
