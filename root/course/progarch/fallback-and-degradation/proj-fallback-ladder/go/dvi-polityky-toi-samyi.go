// READ: терпить застаріле на 2 хв; коли кеш прострочено — чесна відмова (дефолту НЕМА).
var readPolicy = Policy[Reading]{
    Op:           "readState",
    Cache:        readingCache,
    StaleBudget:  2 * time.Minute,
    SmartDefault: nil, // прострочений кеш → Unavailable, а не тихе старе значення
}

func ReadState(id string) (Served[Reading], error) {
    return WithFallback(id, readPolicy, func() (Reading, error) {
        return device.Read(id) // таймаут/запобіжник — усередині
    })
}

// ҐЕЙТ (так/ні): кешу НЕМА (щоб не відтворити застаріле «дозволено»), дефолт = fail-closed.
// Для пейволла було б SmartDefault: func() Decision { return Decision{Allowed: true} }.
var unlockGatePolicy = Policy[Decision]{
    Op:           "canCommand:unlock",
    Cache:        nil,
    SmartDefault: func() Decision { return Decision{Allowed: false} }, // fail-closed
}

func Unlock(user, id string) error {
    gate, err := WithFallback(user+":"+id, unlockGatePolicy, func() (Decision, error) {
        return authz.CanCommand(user, id, "unlock")
    })
    if err != nil {
        return err // напр., не-залежницька помилка авторизації — пропускаємо як є
    }
    if !gate.Value.Allowed {
        return &Forbidden{User: user, ID: id} // fail-closed: не впустили — правильно
    }
    return hub.Send(id, "unlock") // саму команду не фолбечимо — вона не ідемпотентна
}
