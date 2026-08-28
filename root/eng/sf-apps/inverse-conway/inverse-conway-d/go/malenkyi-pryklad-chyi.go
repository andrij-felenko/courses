// Одна команда володіє обома підсистемами — межі немає,
// тож найдешевше просто ділити внутрішній стан під спільним замком.
type Cache struct {
	Mu   sync.Mutex
	Data map[Key]Value // усе назовні, будь-хто чіпає напряму
}

// billing.go і catalog.go обидва роблять так:
cache.Mu.Lock()
cache.Data[k] = v // прямий доступ до нутра
cache.Mu.Unlock()
