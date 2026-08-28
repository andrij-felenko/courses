// Один щабель драбини: жива відповідь → інакше кеш у межах бюджету застарілості.
func ReadState(ctx context.Context, id string) (Reading, error) {
    fresh, err := device.Read(ctx, id) // запобіжник/таймаут — усередині
    if err == nil {
        cache.Put(id, fresh, time.Now()) // тримаємо копію теплою
        return fresh, nil
    }
    if c, ok := cache.Get(id); ok && time.Since(c.At) <= staleBudget {
        metrics.Inc("fallback.cache", id) // деградуємо ГОЛОСНО (нижче)
        c.Value.Stale = true
        return c.Value, nil
    }
    return Reading{}, ErrUnavailable // кеш надто старий — чесна відмова
}
