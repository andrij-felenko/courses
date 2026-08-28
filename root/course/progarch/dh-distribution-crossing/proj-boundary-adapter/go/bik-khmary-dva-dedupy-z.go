// ── БІК ХМАРИ: тут живе дедуп — друга половина «фактично раз». ──
type CloudServer struct {
	mu       sync.Mutex
	seen     map[string]Result // ключ ідемпотентності → кешований результат
	lastTS   map[string]int64  // dev|field → найсвіжіша бачена мітка
	state    map[string]string // dev → востаннє почуте значення
	executed int               // скільки КОМАНД реально виконано
	applied  int               // скільки ЗВІТІВ реально застосовано
}
func NewCloudServer() *CloudServer {
	return &CloudServer{seen: map[string]Result{}, lastTS: map[string]int64{}, state: map[string]string{}}
}

// Команда: той самий ключ → той самий результат, дію НЕ повторюємо.
func (s *CloudServer) HandleCmd(cmd Command) Result {
	s.mu.Lock()
	defer s.mu.Unlock()
	if r, ok := s.seen[cmd.Key]; ok {
		return r // ДУБЛЬ повтору — нічого не робимо
	}
	s.executed++ // виконуємо РІВНО раз
	if cmd.Kind == "setState" {
		s.state[cmd.Dev] = cmd.Arg
	}
	r := Result{OK: true, Note: "виконано " + cmd.Kind}
	s.seen[cmd.Key] = r
	return r
}

// Звіт: одне правило ловить і дубль, і спізнілий реордер.
func (s *CloudServer) HandleReport(rep Report) {
	s.mu.Lock()
	defer s.mu.Unlock()
	k := rep.Dev + "|" + rep.Field
	if rep.TS <= s.lastTS[k] { // ≤ бачене → дубль АБО старіший реордер
		return
	}
	s.lastTS[k] = rep.TS // свіжіша мітка виграла
	s.state[rep.Dev] = rep.Value
	s.applied++
}
func (s *CloudServer) State(dev string) string { s.mu.Lock(); defer s.mu.Unlock(); return s.state[dev] }
func (s *CloudServer) Applied() int            { s.mu.Lock(); defer s.mu.Unlock(); return s.applied }
