package migration

import (
	"sync"
	"sync/atomic"
	"time"
)

// Entry — знімок одного викликальника: скільки разів і коли востаннє.
type Entry struct {
	Count    uint64
	LastSeen time.Time
}

// DeprecationMeter — телеметрія одного застарілого шляху.
// Живе стільки, скільки вікно міграції.
type DeprecationMeter struct {
	// Лічильник — гарячий шлях: лише атомарний інкремент, без замка.
	// atomic.Uint64 дає ту саму неподільність, що LOCK XADD; порядку
	// щодо іншої пам'яті нам не треба — це просто підрахунок.
	hits atomic.Uint64

	// Реєстр «хто саме» — холодний бік: рідко читаємо, можна під замком.
	// Тут дані складніші за число, тож атоміком не обійтися.
	mu      sync.Mutex
	callers map[string]Entry
}

func NewDeprecationMeter() *DeprecationMeter {
	return &DeprecationMeter{callers: make(map[string]Entry)}
}

// Record викликається на КОЖНЕ звернення до старого шляху — має бути дешевим.
func (m *DeprecationMeter) Record(caller string) {
	m.hits.Add(1) // гарячий шлях: атомарний інкремент без замка

	m.mu.Lock()
	defer m.mu.Unlock()
	e := m.callers[caller]
	e.Count++
	e.LastSeen = time.Now()
	m.callers[caller] = e
}

// Hits — скільки разів старим шляхом скористалися за поточне вікно.
func (m *DeprecationMeter) Hits() uint64 {
	return m.hits.Load()
}

// Snapshot — знімок «хто ще ходить», щоб піти й допомогти саме цим клієнтам.
func (m *DeprecationMeter) Snapshot() map[string]Entry {
	m.mu.Lock()
	defer m.mu.Unlock()
	out := make(map[string]Entry, len(m.callers))
	for k, v := range m.callers {
		out[k] = v // копія під замком — безпечно віддати назовні
	}
	return out
}

// Reset обнуляє на початку нового вікна вимірювання (напр. щодоби).
func (m *DeprecationMeter) Reset() {
	m.hits.Store(0)
	m.mu.Lock()
	defer m.mu.Unlock()
	m.callers = make(map[string]Entry)
}
