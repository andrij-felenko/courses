package migration

import "time"

// RemovalGate — рішення прибирати ухвалюють НЕ за датою, а за порожнім вікном.
type RemovalGate struct {
	meter       *DeprecationMeter
	quietNeeded time.Duration
	// zeroSince — момент, відколи триває тиша; nil, коли зараз є користувачі.
	zeroSince *time.Time
}

func NewRemovalGate(m *DeprecationMeter, quietNeeded time.Duration) *RemovalGate {
	if quietNeeded == 0 {
		quietNeeded = 24 * 14 * time.Hour // два тижні за замовчуванням
	}
	return &RemovalGate{meter: m, quietNeeded: quietNeeded}
}

// Poll кличемо періодично (напр. раз на годину зі спостерігача).
// Стежимо, чи лічильник ТРИМАЄ нуль достатньо довго.
func (g *RemovalGate) Poll() {
	if g.meter.Hits() == 0 {
		if g.zeroSince == nil {
			now := time.Now()
			g.zeroSince = &now // нуль щойно почався
		}
		// інакше — нуль триває, момент початку не чіпаємо
	} else {
		g.zeroSince = nil // хтось прийшов — відлік скинуто
	}
	g.meter.Reset() // нове вікно вимірювання
}

// SafeToRemove: безпечно прибирати ⟺ нуль протримався не менше quietNeeded.
func (g *RemovalGate) SafeToRemove() bool {
	if g.zeroSince == nil {
		return false // зараз є користувачі
	}
	return time.Since(*g.zeroSince) >= g.quietNeeded
}
