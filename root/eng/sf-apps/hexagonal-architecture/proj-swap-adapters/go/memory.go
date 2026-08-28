// adapters/memory.go ── ДРАЙВОВАНИЙ АДАПТЕР. Той самий порт, але в пам'яті.
package adapters

import (
    "sync"

    "example/order"
)

type ПамятьСховище struct {
    mu   sync.RWMutex
    дані map[string]order.Замовлення
}

func НовеПамятьСховище() *ПамятьСховище {
    return &ПамятьСховище{дані: map[string]order.Замовлення{}}
}

func (r *ПамятьСховище) Зберегти(з order.Замовлення) error {
    r.mu.Lock()
    defer r.mu.Unlock()
    r.дані[з.ID] = з // усе «сховище» — одна мапа
    return nil
}

func (r *ПамятьСховище) Узяти(id string) (*order.Замовлення, error) {
    r.mu.RLock()
    defer r.mu.RUnlock()
    if з, ok := r.дані[id]; ok {
        return &з, nil
    }
    return nil, nil
}
