type NetworkCloud struct {
	wire Wire
	mu   sync.Mutex
	buf  []Report      // черга непідтверджених звітів (FIFO)
	sig  chan struct{} // будильник флашера
}
func NewNetworkCloud(w Wire) *NetworkCloud { return &NetworkCloud{wire: w, sig: make(chan struct{}, 1)} }

// КОМАНДА: бюджет часу + повтор із відступом і джитером; ключ СТАЛИЙ крізь спроби.
func (c *NetworkCloud) Send(ctx context.Context, cmd Command) (Result, error) {
	ctx, cancel := context.WithTimeout(ctx, 10*time.Second) // монотонний дедлайн
	defer cancel()
	const base, capD = 100 * time.Millisecond, 3 * time.Second
	for attempt := 0; ; attempt++ {
		res, err := c.wire.PostCmd(ctx, cmd) // той самий cmd.Key щоразу
		if err == nil || !errors.Is(err, ErrUnreachable) {
			return res, err // успіх або невиправна помилка — не повторюємо
		}
		w := base << attempt
		if w <= 0 || w > capD { // <=0 ловить переповнення зсуву на великому attempt
			w = capD
		}
		wait := time.Duration(rand.Int64N(int64(w))) // повний джитер: рівномірно [0, вікно)
		if dl, ok := ctx.Deadline(); ok && time.Until(dl) < wait {
			return res, fmt.Errorf("бюджет вичерпано: %w", err) // не спати за дедлайн
		}
		select {
		case <-time.After(wait):
		case <-ctx.Done():
			return res, ctx.Err()
		}
	}
}

// ЗВІТ (гарячий шлях): у буфер і НЕГАЙНО назад — мережі не торкаємось.
func (c *NetworkCloud) Emit(rep Report) {
	c.mu.Lock()
	c.buf = append(c.buf, rep)
	c.mu.Unlock()
	select {
	case c.sig <- struct{}{}: // штовхнути флашер, не блокуючись
	default:
	}
}

// Фоновий флашер: доки хмара мовчить — тримає; ожила — досилає по черзі.
func (c *NetworkCloud) FlushLoop(ctx context.Context) {
	tick := time.NewTicker(500 * time.Millisecond)
	defer tick.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-c.sig: // прокинувся на новому звіті
		case <-tick.C: // …або сам, раз на 500 мс
		}
		c.drain(ctx)
	}
}

func (c *NetworkCloud) drain(ctx context.Context) {
	for {
		c.mu.Lock()
		if len(c.buf) == 0 {
			c.mu.Unlock()
			return
		}
		head := c.buf[0] // лише флашер знімає з голови → голова стабільна
		c.mu.Unlock()

		sendCtx, cancel := context.WithTimeout(ctx, 2*time.Second)
		err := c.wire.PostReport(sendCtx, head)
		cancel()
		if err != nil {
			return // хмара мовчить/ACK не дійшов — лишаємо в буфері, спробуємо пізніше
		}
		c.mu.Lock()
		c.buf = c.buf[1:] // ACK отримано — АЖ ТЕПЕР знімаємо голову
		c.mu.Unlock()
	}
}

func (c *NetworkCloud) Pending() int { c.mu.Lock(); defer c.mu.Unlock(); return len(c.buf) }
func (c *NetworkCloud) ReadState(ctx context.Context, dev string) (string, error) {
	return c.wire.GetState(ctx, dev)
}
