type SensorUnavailable struct {
    Room  string
    Cause error
}
func (e *SensorUnavailable) Error() string {
    return fmt.Sprintf("давач у кімнаті %q недоступний", e.Room)
}
func (e *SensorUnavailable) Unwrap() error { return e.Cause }   // зберегли причину

func readTemp(room string) (float64, error) {   // помилка — звичайне значення
    var last error
    for i := 0; i < 2; i++ {                     // одна повторна спроба
        t, err := i2cRead(room)
        if err == nil {
            return t, nil
        }
        last = err
    }
    return 0, &SensorUnavailable{Room: room, Cause: last}   // переклали вгору
}

// політика:
for _, room := range rooms {
    t, err := readTemp(room)
    if err != nil {
        log.Printf("тримаю стан: %v", err)   // лог РАЗ, саме тут
        continue                             // обігрівач цієї кімнати не чіпаємо
    }
    applyPolicy(room, t)
}
