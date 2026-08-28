// Hub — «хаб у передпокої». Виконує команди й лічить КОЖНЕ спрацювання реле.
// fires — не про наміри клієнта, а про фізику: скільки разів двері клацнули.
type Hub struct {
	mu    sync.Mutex
	open  bool // стан замка №7
	fires int  // ← слід кожного смикання реле; це наш детектор правди
}

func (h *Hub) unlock() {
	h.mu.Lock()
	defer h.mu.Unlock()
	h.open = true
	h.fires++
}

func (h *Hub) state() string { // «замок №7 зараз який?»
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.open {
		return "відчинено"
	}
	return "замкнено"
}

func (h *Hub) firesCount() int {
	h.mu.Lock()
	defer h.mu.Unlock()
	return h.fires
}
