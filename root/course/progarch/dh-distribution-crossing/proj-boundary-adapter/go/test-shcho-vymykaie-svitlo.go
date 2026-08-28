// Фейковий Wire: можна «вимкнути» (silent) і один раз «загубити ACK» звіту.
type fakeWire struct {
	srv         *CloudServer
	silent      atomic.Bool
	dropAckOnce atomic.Bool // раз: звіт застосовано, але ACK не повернено → хаб повторить
}
func (w *fakeWire) PostCmd(ctx context.Context, cmd Command) (Result, error) {
	if w.silent.Load() {
		return Result{}, ErrUnreachable
	}
	return w.srv.HandleCmd(cmd), nil
}
func (w *fakeWire) PostReport(ctx context.Context, rep Report) error {
	if w.silent.Load() {
		return ErrUnreachable // хмара мовчить — доставки нема
	}
	w.srv.HandleReport(rep) // дійшло й ЗАСТОСОВАНО
	if w.dropAckOnce.CompareAndSwap(true, false) {
		return ErrUnreachable // …але ACK загублено → хаб вважатиме невдачею й повторить
	}
	return nil
}
func (w *fakeWire) GetState(ctx context.Context, dev string) (string, error) {
	if w.silent.Load() {
		return "", ErrUnreachable
	}
	return w.srv.State(dev), nil
}

// Життєвий контур: кнопка → хаб → замок. Жодного посилання на Wire — суто локальний.
type Hub struct {
	cloud *NetworkCloud
	mu    sync.Mutex
	lock  string
	tick  int64
}
func (h *Hub) Press(open bool) {
	h.mu.Lock()
	if open {
		h.lock = "open"
	} else {
		h.lock = "closed"
	}
	h.tick++
	rep := Report{Dev: "lock-42", Field: "lock", Value: h.lock, TS: h.tick}
	h.mu.Unlock()
	h.cloud.Emit(rep) // замок уже клацнув; звіт лише кладемо в буфер
}
func (h *Hub) Lock() string { h.mu.Lock(); defer h.mu.Unlock(); return h.lock }

func TestBoundarySurvivesSilence(t *testing.T) {
	srv := NewCloudServer()
	wire := &fakeWire{srv: srv}
	wire.dropAckOnce.Store(true) // озброїмо один загублений ACK — щоб виник СПРАВЖНІЙ дубль
	cloud := NewNetworkCloud(wire)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	go cloud.FlushLoop(ctx)
	hub := &Hub{cloud: cloud}

	const N = 20
	pendingMid := 0
	for i := 1; i <= N; i++ {
		switch i {
		case 5:
			wire.silent.Store(true) // ← хмара впала ПОСЕРЕД потоку
		case 14:
			pendingMid = cloud.Pending() // буфер має тримати непідтверджені
		case 15:
			wire.silent.Store(false) // ← зв'язок вернувся
		}
		hub.Press(i%2 == 0)
		time.Sleep(2 * time.Millisecond) // хай флашер устигне щось доставити до тиші
	}

	// 1) Життєвий контур не здригнувся: локальний стан = останнє натискання.
	want := "closed"
	if N%2 == 0 {
		want = "open"
	}
	if got := hub.Lock(); got != want {
		t.Fatalf("контур удома здригнувся: lock=%q, чекали %q", got, want)
	}
	// 2) Store-and-forward справді тримав звіти, поки хмара мовчала.
	if pendingMid == 0 {
		t.Fatalf("буфер мав тримати звіти під час тиші, а він порожній")
	}
	// 3) Зв'язок вернувся — чекаємо, поки буфер долетить.
	deadline := time.Now().Add(5 * time.Second)
	for cloud.Pending() > 0 && time.Now().Before(deadline) {
		time.Sleep(5 * time.Millisecond)
	}
	if p := cloud.Pending(); p != 0 {
		t.Fatalf("буфер не спорожнів: лишилось %d", p)
	}
	// 4) Кожен звіт застосовано РІВНО раз (попри тишу й один загублений ACK).
	if srv.Applied() != N {
		t.Fatalf("«фактично раз» порушено: застосовано %d, а натискань %d", srv.Applied(), N)
	}
	// 5) Хмара догнала дім.
	if got := srv.State("lock-42"); got != want {
		t.Fatalf("хмара не збіглася з домом: %q проти %q", got, want)
	}
}
