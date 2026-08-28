package kv

const (
	fnvOffset = 2166136261
	fnvPrime  = 16777619
	initCap   = 8 // степінь двійки
)

type node struct {
	key  string
	val  int
	next *node
}

type Map struct {
	buckets []*node
	n       int
}

func New() *Map { return &Map{buckets: make([]*node, initCap)} }

// FNV-1a + домішування старших бітів у молодші.
// Індексуємо БАЙТИ: key[i] — це байт. А `for _, r := range key` віддавало б
// руни, і на не-ASCII ключах хеш вийшов би інший.
func hash(key string) uint32 {
	h := uint32(fnvOffset)
	for i := 0; i < len(key); i++ {
		h ^= uint32(key[i])
		h *= fnvPrime // переповнення uint32 тут навмисне
	}
	return h ^ (h >> 16)
}

func (m *Map) index(h uint32) int { return int(h & uint32(len(m.buckets)-1)) }

func (m *Map) Get(key string) (int, bool) {
	for p := m.buckets[m.index(hash(key))]; p != nil; p = p.next {
		if p.key == key { // звіряємо ПОВНИЙ ключ, не хеш
			return p.val, true
		}
	}
	return 0, false
}

func (m *Map) Put(key string, val int) {
	i := m.index(hash(key))
	for p := m.buckets[i]; p != nil; p = p.next {
		if p.key == key {
			p.val = val // оновлення наявного: n НЕ росте
			return
		}
	}
	m.buckets[i] = &node{key: key, val: val, next: m.buckets[i]} // у голову
	m.n++
	if 4*m.n > 3*len(m.buckets) { // α > 0.75
		m.grow()
	}
}

func (m *Map) Delete(key string) bool {
	i := m.index(hash(key))
	var prev *node
	for p := m.buckets[i]; p != nil; p = p.next {
		if p.key == key {
			if prev == nil {
				m.buckets[i] = p.next // видаляємо голову
			} else {
				prev.next = p.next
			}
			m.n--
			return true
		}
		prev = p
	}
	return false
}

func (m *Map) grow() {
	old := m.buckets
	m.buckets = make([]*node, len(old)*2) // нова місткість — ДО переіндексації
	for _, head := range old {
		for p := head; p != nil; {
			next := p.next // зберегти: зараз перечепимо p.next
			i := m.index(hash(p.key))
			p.next = m.buckets[i]
			m.buckets[i] = p
			p = next
		}
	}
	// m.n не чіпаємо: пари переїхали, нових не з'явилося
}

func (m *Map) Len() int { return m.n }
