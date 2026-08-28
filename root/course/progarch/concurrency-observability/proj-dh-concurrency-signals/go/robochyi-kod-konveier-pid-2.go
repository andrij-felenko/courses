type Pool struct {
	jobs   chan Job                       // буфер = черга; len — насиченість, cap — стеля
	handle func(context.Context, Command) // корисна робота: виклик до пристрою

	busy      atomic.Int64 // зайнятих робітників
	live      atomic.Int64 // L: у черзі + в обробці
	accepted  atomic.Int64 // скільки задач впустили (для λ)
	done      atomic.Int64 // скільки завершили (для W)
	sojournNs atomic.Int64 // сума W у наносекундах (для W)
	brake     atomic.Bool  // прапор протитиску: край читає його ПЕРЕД впуском
}

func New(workers, buffer int, handle func(context.Context, Command)) *Pool {
	p := &Pool{jobs: make(chan Job, buffer), handle: handle}
	poolSize.Set(float64(workers))
	for i := 0; i < workers; i++ {
		go p.worker()
	}
	go p.observe(time.Second)
	return p
}

// Submit — край кладе команду в чергу, але СПЕРШУ питає протитиск.
func (p *Pool) Submit(cmd Command) bool {
	if p.brake.Load() {
		return false // протитиск: чесно відмовляємо, а не роздуваємо чергу мовчки
	}
	select {
	case p.jobs <- Job{Cmd: cmd, enqueued: time.Now()}: // МОНОТОННИЙ штамп
		p.accepted.Add(1)
		p.live.Add(1) // +1 до L: задача ввійшла в систему
		return true
	default:
		return false // буфер повний — теж відмова, а не блокування краю
	}
}

func (p *Pool) worker() {
	for j := range p.jobs {
		p.busy.Add(1)
		p.handle(context.Background(), j.Cmd)
		// W рахуємо ВІД enqueue. time.Since читає МОНОТОННИЙ годинник —
		// імунний до стрибка настінного часу посеред виміру.
		d := time.Since(j.enqueued)
		sojourn.WithLabelValues(j.Cmd.Name).Observe(d.Seconds())
		p.sojournNs.Add(d.Nanoseconds())
		p.done.Add(1)
		p.busy.Add(-1)
		p.live.Add(-1) // −1 до L: задача вийшла
	}
}
