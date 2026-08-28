// max_age_ms — контракт свіжості: наскільки застарілі дані ми ще
// згодні віддавати. Це ЧИСЛО зі сценарію атрибута, а не випадкова стала.
type Cache struct {
    Value       uint32 // збережена відповідь
    StoredAtMs  uint32 // коли поклали в кеш
    Valid       bool   // чи є що віддавати
}

// Повертаємо (значення, ok) — канонічний Go-аналог «bool + out-параметр».
func (c *Cache) Get(nowMs, maxAgeMs uint32) (uint32, bool) {
    if !c.Valid {
        return 0, false // кеш порожній — доведеться рахувати
    }
    if nowMs-c.StoredAtMs > maxAgeMs {
        return 0, false // застаріло понад дозволене — теж рахувати
    }
    return c.Value, true // свіже — швидкий шлях
}
