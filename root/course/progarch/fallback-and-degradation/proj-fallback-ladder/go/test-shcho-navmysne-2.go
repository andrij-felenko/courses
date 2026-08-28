func TestReadFreshCache(t *testing.T) {
    dev := &fakeDevice{reading: Reading{Temperature: 21.5}}
    policy := readPolicy
    policy.Cache = newMapCache[Reading]()

    // прогрів: жива відповідь осідає в кеш
    WithFallback("dev-1", policy, func() (Reading, error) { return dev.Read("dev-1") })
    dev.down = true // ← вимикаємо залежність

    served, err := WithFallback("dev-1", policy,
        func() (Reading, error) { return dev.Read("dev-1") })

    if err != nil {
        t.Fatalf("не мало впасти: %v", err)
    }
    if served.Rung != RungCache {
        t.Errorf("щабель = %q, хотіли cache", served.Rung)
    }
    if !served.Stale {
        t.Error("cache-щабель мусить нести stale=true")
    }
}

func TestReadExpiredCacheFailsHonestly(t *testing.T) {
    dev := &fakeDevice{down: true}
    cache := newMapCache[Reading]()
    cache.seed("dev-1", Reading{Temperature: 21.5}, time.Now().Add(-5*time.Minute)) // кешу 5 хв
    policy := readPolicy
    policy.Cache = cache
    policy.StaleBudget = time.Minute // бюджет 1 хв < вік кешу

    _, err := WithFallback("dev-1", policy,
        func() (Reading, error) { return dev.Read("dev-1") })

    var un *Unavailable
    if !errors.As(err, &un) { // мусить бути ЧЕСНА відмова, а не старе значення
        t.Fatalf("хотіли Unavailable, а не стару брехню; отримали %v", err)
    }
}

func TestGateFailClosed(t *testing.T) {
    served, err := WithFallback("u1:dev-1", unlockGatePolicy,
        func() (Decision, error) { return Decision{}, &TimeoutError{Key: "authz"} })

    if err != nil {
        t.Fatalf("ґейт не мав повернути помилку: %v", err)
    }
    if served.Rung != RungDefault {
        t.Errorf("щабель = %q, хотіли default", served.Rung)
    }
    if served.Value.Allowed { // fail-closed: дефолт мусить бути ЗАБОРОНА
        t.Error("fail-closed зламано: дефолт відчинив замок")
    }
}
