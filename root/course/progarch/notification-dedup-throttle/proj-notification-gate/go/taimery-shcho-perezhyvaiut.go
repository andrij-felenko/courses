// Довговічний варіант: дедлайн — у спільному індексі, а не лише в пам'яті.
func (g *Gate) armDurable(ctx context.Context, group, class string) {
	// Кладемо мить флашу в індекс за часом (ZADD). Переживе перезапуск інстанса.
	_ = g.store.MarkDue(ctx, group, g.now().Add(g.window))
	// Локальний таймер лишаємо як швидкий шлях; спрацювавши — сам прибирає дедлайн.
	g.timers.Store(group, g.sched(g.window, func() {
		g.flushDue(context.Background(), group, class)
	}))
}

// flushDue — флаш плюс прибирання дедлайну з індексу (ZREM). Спільний для
// швидкого шляху (локальний таймер) і підмітальника, тож індекс чиститься в обох.
func (g *Gate) flushDue(ctx context.Context, group, class string) {
	if err := g.flush(ctx, group, class); err == nil {
		_ = g.store.ClearDue(ctx, group) // зведено успішно → більше не спливе
	}
}

// sweep — крутиться в КОЖНОМУ інстансі. Бере з індексу прострочені групи й флашить
// ту, яку вдалося застовпити АТОМАРНО (claim), щоб флашив лише один інстанс.
func (g *Gate) sweep(ctx context.Context) {
	due, err := g.store.DueGroups(ctx, g.now()) // групи, чий дедлайн у індексі сплив
	if err != nil {
		return
	}
	for _, group := range due {
		claimed, _ := g.store.SetNX(ctx, "flushing:"+group, 30*time.Second)
		if claimed {
			g.flushDue(ctx, group, classOf(group))
		}
	}
}
