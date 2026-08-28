// загальна форма: атомарно застосувати f до значення через compare-and-swap
func (e *EventIds) Update(f func(uint64) uint64) uint64 {
    for {
        old := e.next.Load()
        neu := f(old)
        if e.next.CompareAndSwap(old, neu) {  // вдалося лише якщо ніхто не змінив old
            return neu
        }
        // хтось випередив між Load і CompareAndSwap → пробуємо ще раз
    }
}
