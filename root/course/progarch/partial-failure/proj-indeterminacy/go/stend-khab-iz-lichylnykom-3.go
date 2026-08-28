// clientUnlock шле «відчини замок №7» і чекає НЕ довше patience.
// На таймауті повертає помилку — не знаючи, ЩО там сталося.
func clientUnlock(l *Link, h *Hub, patience time.Duration) error {
	reply := l.send(func() string { h.unlock(); return "ok" })
	select {
	case <-reply:
		return nil // почули «ok» — успіх
	case <-time.After(patience):
		return errors.New("таймаут") // тиша. Котрий зі світів — невідомо.
	}
}
