// Який щабель драбини віддав відповідь — рівно ці чотири.
type Rung string

const (
    RungLive        Rung = "live"
    RungCache       Rung = "cache"
    RungDefault     Rung = "default"
    RungUnavailable Rung = "unavailable"
)

// Те, що обгортка ЗАВЖДИ повертає: значення, щабель і чи воно застаріле.
type Served[T any] struct {
    Value T
    Rung  Rung
    Stale bool
}

type entry[T any] struct {
    value T
    at    time.Time
}
type Cache[T any] interface {
    Get(key string) (entry[T], bool)
    Put(key string, v T)
}

// Policy — це драбина В ДАНИХ: які щаблі ввімкнені саме для ЦЬОГО виклику.
type Policy[T any] struct {
    Op           string        // ім'я для метрик
    Cache        Cache[T]      // nil → щабель кешу вимкнено
    StaleBudget  time.Duration // кеш віддаємо, лише поки вік ≤ цього
    SmartDefault func() T      // nil → дефолту нема; для ґейта це fail-open/closed
}
