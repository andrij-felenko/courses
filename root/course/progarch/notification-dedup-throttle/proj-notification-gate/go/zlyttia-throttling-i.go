func (g *Gate) arm(group, class string) {
	// g.sched — інжектований планувальник (у проді time.AfterFunc; у тесті — ручний).
	t := g.sched(g.window, func() { _ = g.flush(context.Background(), group, class) })
	g.timers.Store(group, t)
}

func (g *Gate) flush(ctx context.Context, group, class string) error {
	g.timers.Delete(group)
	raw, err := g.store.Drain(ctx, group) // забрати й очистити буфер за один крок
	if err != nil || len(raw) == 0 {
		return err
	}
	batch := make([]Notification, 0, len(raw))
	for _, b := range raw {
		var n Notification
		if json.Unmarshal(b, &n) == nil {
			batch = append(batch, n)
		}
	}
	user, channel := batch[0].Recipient, batch[0].Channel

	// Тихі години — настінний МІСЦЕВИЙ час користувача (не UTC, не монотонний!).
	if g.quiet(user, g.now()) {
		return g.rebuffer(ctx, batch) // притримати до ранку → спокійний ранковий дайджест
	}

	// Стеля темпу — на пару (user,channel). Годинник відра — самого сховища.
	ok, err := g.store.Take(ctx, "tb:"+user+":"+channel, g.burst, g.rate)
	if err != nil {
		return err
	}
	if !ok {
		return g.ladder(ctx, class, batch) // порожнє відро → драбина, не мовчазне «відкинути»
	}
	return g.deliver(ctx, digest(class, batch, g.render, channel))
}

func digest(class string, batch []Notification, render func(string, []Notification) string, channel string) Notification {
	return Notification{
		Recipient: batch[0].Recipient,
		Channel:   channel,
		Severity:  Warning,
		At:        batch[len(batch)-1].At,
		Text:      render(class, batch), // "40 пристроїв втратили зв'язок" — робота шаблонів
	}
}
