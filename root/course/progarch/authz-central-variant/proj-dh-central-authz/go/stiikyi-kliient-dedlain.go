// Мінімальний запобіжник: після N поспіль збоїв РОЗМИКАЄМОСЬ на cooldown і не дзвонимо в центр.
type Breaker struct {
	mu        sync.Mutex
	fails     int
	threshold int
	cooldown  time.Duration
	openUntil time.Time
}

func (b *Breaker) Allow() bool {
	b.mu.Lock()
	defer b.mu.Unlock()
	return time.Now().After(b.openUntil) // розімкнено (пропускаємо), доки не мине cooldown
}

func (b *Breaker) Record(ok bool) {
	b.mu.Lock()
	defer b.mu.Unlock()
	if ok {
		b.fails = 0 // успіх «заживляє» лічильник
		return
	}
	if b.fails++; b.fails >= b.threshold {
		b.openUntil = time.Now().Add(b.cooldown) // забагато збоїв поспіль → розмикаємось
		b.fails = 0
	}
}

var ErrBreakerOpen = errors.New("pdp: breaker open")

// Стійкий клієнт до PDP: жорсткий дедлайн + запобіжник. Будь-який збій → помилка нагору,
// а CentralAuthorizer оберне її на deny (fail-closed).
type ResilientPdp struct {
	base    string
	client  *http.Client
	breaker *Breaker
}

func (p *ResilientPdp) Check(ctx context.Context, req Decision) (Verdict, error) {
	if !p.breaker.Allow() {
		return Verdict{}, ErrBreakerOpen // центр «падає» — навіть не дзвонимо, одразу fail-closed
	}
	ctx, cancel := context.WithTimeout(ctx, 150*time.Millisecond) // дедлайн на похід у центр
	defer cancel()

	body, _ := json.Marshal(req)
	httpReq, _ := http.NewRequestWithContext(ctx, http.MethodPost, p.base+"/check", bytes.NewReader(body))
	httpReq.Header.Set("Content-Type", "application/json")

	resp, err := p.client.Do(httpReq)
	if err != nil {
		p.breaker.Record(false) // мережа/таймаут → зараховуємо збій
		return Verdict{}, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		p.breaker.Record(false)
		return Verdict{}, fmt.Errorf("pdp: %s", resp.Status)
	}
	var v Verdict
	if err := json.NewDecoder(resp.Body).Decode(&v); err != nil {
		p.breaker.Record(false)
		return Verdict{}, err
	}
	p.breaker.Record(true) // успіх — «заживає»
	return v, nil
}
