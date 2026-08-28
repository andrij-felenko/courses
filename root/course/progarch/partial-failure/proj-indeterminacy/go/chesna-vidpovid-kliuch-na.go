// KeyedHub — той самий хаб, але команда несе КЛЮЧ. Уже бачений ключ повертає
// збережений результат, не виконуючи ефекту повторно.
type KeyedHub struct {
	mu    sync.Mutex
	open  bool
	fires int
	seen  map[string]string // ключ команди → збережений результат
}

func NewKeyedHub() *KeyedHub { return &KeyedHub{seen: map[string]string{}} }

func (h *KeyedHub) unlock(key string) string {
	h.mu.Lock()
	defer h.mu.Unlock()
	if res, dup := h.seen[key]; dup {
		return res // ДУБЛЬ: віддаємо збережене, реле не чіпаємо
	}
	h.open = true
	h.fires++                     // виконуємо РІВНО раз на ключ
	h.seen[key] = "ok: відчинено" // перевірка → ефект → запис ключа: усе під ОДНИМ замком
	return h.seen[key]
}

func (h *KeyedHub) firesCount() int { h.mu.Lock(); defer h.mu.Unlock(); return h.fires }
