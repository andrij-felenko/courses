type memStore struct {
	mu    sync.Mutex
	keys  map[string]time.Time
	lists map[string][][]byte
	tb    map[string]*tokbucket
	due   map[string]time.Time // ІНДЕКС ДЕДЛАЙНІВ: група → мить флашу (аналог ZSET)
	now   func() time.Time      // ГОДИННИК СХОВИЩА (спільний для всіх інстансів)
}

type tokbucket struct {
	tokens float64
	last   time.Time
}

func (s *memStore) SetNX(_ context.Context, k string, ttl time.Duration) (bool, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if exp, ok := s.keys[k]; ok && s.now().Before(exp) {
		return false, nil // ключ іще живий → ми не перші
	}
	s.keys[k] = s.now().Add(ttl)
	return true, nil
}

func (s *memStore) Append(_ context.Context, g string, item []byte, _ time.Duration) (int, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.lists[g] = append(s.lists[g], item)
	return len(s.lists[g]), nil // довжина ПІСЛЯ додавання — як RPUSH
}

func (s *memStore) Drain(_ context.Context, g string) ([][]byte, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	out := s.lists[g]
	delete(s.lists, g)
	return out, nil
}

func (s *memStore) Take(_ context.Context, key string, burst, rate float64) (bool, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	b := s.tb[key]
	if b == nil {
		b = &tokbucket{tokens: burst, last: s.now()}
		s.tb[key] = b
	}
	b.tokens += s.now().Sub(b.last).Seconds() * rate // дозрів за годинником СХОВИЩА
	if b.tokens > burst {
		b.tokens = burst
	}
	b.last = s.now()
	if b.tokens >= 1 {
		b.tokens--
		return true, nil
	}
	return false, nil
}

// Індекс дедлайнів: у Redis це ZSET, тут — мапа група→мить, скан під мютексом.
func (s *memStore) MarkDue(_ context.Context, group string, at time.Time) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.due[group] = at // ZADD due <at> group
	return nil
}

func (s *memStore) DueGroups(_ context.Context, now time.Time) ([]string, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	var out []string
	for group, deadline := range s.due { // ZRANGEBYSCORE due -inf now
		if !deadline.After(now) {
			out = append(out, group)
		}
	}
	return out, nil
}

func (s *memStore) ClearDue(_ context.Context, group string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	delete(s.due, group) // ZREM due group
	return nil
}
