// reconcile: на таймауті не повторюємо наосліп, а питаємо ПРАВДУ й діємо з неї.
func reconcile(l *Link, h *Hub, patience time.Duration) error {
	if err := clientUnlock(l, h, patience); err == nil {
		return nil // почули «ok» — усе гаразд
	}
	// таймаут: не гадаємо, котрий зі світів справдився. Читаємо стан замка.
	reply := l.send(h.state) // h.state має тип func() string — рівно те, що чекає канал
	select {
	case st := <-reply:
		if st == "відчинено" {
			return nil // замок таки відчинений → команда спрацювала, повтор НЕ потрібен
		}
		return clientUnlock(l, h, patience) // напевно замкнено → повторити тепер безпечно
	case <-time.After(patience):
		return errors.New("стан невідомий: і команда, і звірка не дійшли")
	}
}
