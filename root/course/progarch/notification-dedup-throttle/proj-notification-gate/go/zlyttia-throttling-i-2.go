const maxHolds = 1 // притримати щонайбільше стільки разів, тоді щабель нижче

// ladder — драбина при порожньому відрі: притримати → знизити канал → відкинути.
func (g *Gate) ladder(ctx context.Context, class string, batch []Notification) error {
	switch {
	case batch[0].Holds < maxHolds:
		// Щабель 1: притримати й злити в НАСТУПНИЙ дайджест (throttling → злиття).
		return g.rebuffer(ctx, batch)
	case anyAtLeast(batch, Warning):
		// Щабель 2: знизити канал — не push (світить екран), а тихий запис у стрічці.
		return g.deliver(ctx, digest(class, batch, g.render, "feed"))
	default:
		// Щабель 3: відкинути — лише info, що не варте чекати. Лишаємо слід у метриці.
		g.metricDropped(len(batch))
		return nil
	}
}

// rebuffer — кладемо назад у буфер (кожному +1 притримання); наступне вікно забере.
func (g *Gate) rebuffer(ctx context.Context, batch []Notification) error {
	for i := range batch {
		batch[i].Holds++
		item, _ := json.Marshal(batch[i])
		size, err := g.store.Append(ctx, groupKey(batch[i]), item, 2*g.window)
		if err != nil {
			return err
		}
		if size == 1 {
			g.arm(groupKey(batch[i]), batch[i].Class)
		}
	}
	return nil
}

func anyAtLeast(batch []Notification, s Severity) bool {
	for _, n := range batch {
		if n.Severity >= s {
			return true
		}
	}
	return false
}
