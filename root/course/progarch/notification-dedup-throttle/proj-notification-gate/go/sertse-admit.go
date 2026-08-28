type Outcome int

const (
	Delivered Outcome = iota // пішло зараз: критичне в обхід або готовий дайджест
	Buffered                 // лягло в буфер злиття, чекає вікна
	Dropped                  // дубль або відкинуто драбиною
)

type Decision struct {
	Outcome Outcome
	Reason  string
}

// Admit — ЄДИНИЙ вхід. Рішення про одне сповіщення.
func (g *Gate) Admit(ctx context.Context, n Notification) (Decision, error) {
	// 0. Критичне ріже наскрізь: в обхід дедупу, злиття й throttling.
	//    Дедуп для нього НАВМИСНЕ не робимо — краще зайва копія, ніж проковтнута тривога.
	if n.Severity == Critical {
		if err := g.deliver(ctx, n); err != nil {
			return Decision{}, err
		}
		return Decision{Delivered, "critical-bypass"}, nil
	}

	// 1. Дедуп: перший, хто застовпив ключ, — шле; решта тихо мовчить.
	first, err := g.store.SetNX(ctx, dedupKey(n), g.dedupTTL(n))
	if err != nil {
		return Decision{}, err
	}
	if !first {
		return Decision{Dropped, "duplicate"}, nil
	}

	// 2. Злиття: кладемо у СПІЛЬНИЙ буфер групи. Хто дістав довжину 1 —
	//    той відкрив групу й ЄДИНИЙ озброює таймер (атомарний вибір власника).
	item, _ := json.Marshal(n)
	size, err := g.store.Append(ctx, groupKey(n), item, 2*g.window)
	if err != nil {
		return Decision{}, err
	}
	if size == 1 {
		g.arm(groupKey(n), n.Class)
	}
	return Decision{Buffered, "coalescing"}, nil
}
