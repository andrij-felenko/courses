// Замок видає СТРОГО зростаючі жетони. Це і є вся монотонність — маленький
// лічильник, яким керуємо МИ, а не годинник.
type LockService struct{ token uint64 }

func (l *LockService) Acquire() uint64 {
	return atomic.AddUint64(&l.token, 1) // 1, 2, 3, … — атомарно, ніколи не назад
}

// Сховище приймає запис, ЛИШЕ якщо жетон новіший за все бачене.
type Storage struct {
	mu      sync.Mutex
	highest uint64 // найбільший жетон, який уже приймали
	value   string
}

func (s *Storage) Write(token uint64, val string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if token < s.highest { // строго старіший за бачене → застряглий власник
		return fmt.Errorf("застарілий жетон %d < вже бачений %d: запис відкинуто",
			token, s.highest)
	}
	s.highest = token // рухаємо загорожу вгору
	s.value = val
	return nil
}
