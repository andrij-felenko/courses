type Unavailable struct{ Op, Key string }

func (e *Unavailable) Error() string {
    return fmt.Sprintf("%s(%s): залежність недоступна, чесного щабля не лишилось", e.Op, e.Key)
}

// Обгортка віддає НАЙВИЩИЙ щабель, що policy тримає чесно.
func WithFallback[T any](
    key string,
    policy Policy[T],
    primary func() (T, error),
) (Served[T], error) {
    // ① Живий щабель. Таймаут і запобіжник — усередині primary().
    value, err := primary()
    if err == nil {
        if policy.Cache != nil {
            policy.Cache.Put(key, value) // тримаємо копію теплою
        }
        recordRung(policy.Op, RungLive, 0) // метрика на КОЖНОМУ виході, навіть успішному
        return Served[T]{Value: value, Rung: RungLive}, nil
    }

    // КЛЮЧОВЕ: fallback — лише на «залежність мовчить». Баг/валідація летять далі.
    if !isDependencyDown(err) {
        return Served[T]{}, err
    }

    // ② Кеш у межах бюджету застарілості.
    if policy.Cache != nil {
        if hit, ok := policy.Cache.Get(key); ok {
            if age := time.Since(hit.at); age <= policy.StaleBudget {
                recordRung(policy.Op, RungCache, age)
                return Served[T]{Value: hit.value, Rung: RungCache, Stale: true}, nil
            }
        }
    }

    // ③ Розумний дефолт. Для ґейта САМЕ ТУТ живе fail-open/fail-closed.
    if policy.SmartDefault != nil {
        recordRung(policy.Op, RungDefault, 0)
        return Served[T]{Value: policy.SmartDefault(), Rung: RungDefault, Stale: true}, nil
    }

    // ④ Чесна вузька відмова. Не брехня простроченим кешем — прямо «недоступно».
    recordRung(policy.Op, RungUnavailable, 0)
    return Served[T]{}, &Unavailable{Op: policy.Op, Key: key}
}
