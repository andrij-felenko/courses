// ✅ Бюджет на монотонному годиннику
type Budget struct {
	start time.Time     // time.Now() несе В СОБІ монотонне читання
	total time.Duration
}

func NewBudget(total time.Duration) Budget {
	return Budget{start: time.Now(), total: total}
}

// time.Since = time.Now().Sub(start) → віднімання бере МОНОТОННУ складову.
// Стрибок настінного годинника не чіпає цього числа взагалі.
func (b Budget) Remaining() time.Duration { return b.total - time.Since(b.start) }
func (b Budget) Expired() bool            { return b.Remaining() <= 0 }

// Ланцюг під ОДНИМ дедлайном: context несе його крізь усі кроки, а кожен
// крок дістає з ctx рівно свій залишок від 30 секунд.
func FetchReading(ctx context.Context, addr string) (Reading, error) {
	// WithTimeout будує дедлайн від time.Now() (з монотонним читанням)
	// і ставить таймер рантайму — стрибок настінного часу його не зрушить.
	ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
	defer cancel()

	conn, err := connect(ctx, addr) // крок 1 з'їдає частину бюджету — наступним лишиться менше
	if err != nil {
		return Reading{}, err
	}
	defer conn.Close()

	raw, err := readFrame(ctx, conn) // крок 2 бачить залишок ПІСЛЯ connect
	if err != nil {
		return Reading{}, err
	}
	return parse(ctx, raw) // крок 3 — те, що лишилось від 30 с
}

func connect(ctx context.Context, addr string) (net.Conn, error) {
	var d net.Dialer
	return d.DialContext(ctx, "tcp", addr) // dialer сам поважає дедлайн з ctx
}

func readFrame(ctx context.Context, conn net.Conn) ([]byte, error) {
	if dl, ok := ctx.Deadline(); ok {
		conn.SetReadDeadline(dl) // перекладаємо СПІЛЬНИЙ дедлайн на сокет
	}
	buf := make([]byte, 4096)
	n, err := conn.Read(buf)
	return buf[:n], err
}
