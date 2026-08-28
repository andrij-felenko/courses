func TestCoalesceRaceGivesOneDigest(t *testing.T) {
	st := newMemStore(func() time.Time { return t0 }) // ОДНЕ спільне сховище

	var mu sync.Mutex
	digests := 0
	deliver := func(_ context.Context, _ Notification) error {
		mu.Lock()
		digests++
		mu.Unlock()
		return nil
	}
	schedA, schedB := &fakeSched{}, &fakeSched{}
	a := newGateWith(st, deliver, schedA.schedule)
	b := newGateWith(st, deliver, schedB.schedule)

	off := func(id string) Notification {
		return Notification{Recipient: "petrenko", Event: "offline:" + id,
			Class: "connectivity", Channel: "push", Severity: Warning}
	}
	ctx := context.Background()
	_, _ = a.Admit(ctx, off("lamp"))  // A: RPUSH→1 → власник, озброїв таймер у schedA
	_, _ = b.Admit(ctx, off("lock"))  // B: RPUSH→2 → лише додав
	_, _ = a.Admit(ctx, off("therm")) // A: RPUSH→3 → лише додав

	schedA.fireAll() // доганяємо вікно власника
	schedB.fireAll() // у B нема озброєних таймерів — і добре

	if digests != 1 {
		t.Fatalf("та сама група мала дати 1 дайджест, дала %d", digests)
	}
}
