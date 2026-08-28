type TokenBucket struct {
	tokens   float64
	capacity float64 // b — скільки можна поспіль
	refill   float64 // r — жетонів на секунду
	last     time.Time
}

// Allow списує жетон і повертає true, якщо він є.
func (b *TokenBucket) Allow(now time.Time) bool {
	b.tokens += now.Sub(b.last).Seconds() * b.refill
	if b.tokens > b.capacity {
		b.tokens = b.capacity
	}
	b.last = now
	if b.tokens >= 1 {
		b.tokens--
		return true
	}
	return false // порожньо → притримати / злити / відкинути
}
