// ─── тип повідомлення — єдиний «конверт» для будь-яких даних ─────────
type MsgType uint8

const (
    MsgSample MsgType = iota
    MsgButton
    MsgSetMode
)

type Msg struct {
    Type  MsgType
    Value int32
}

// ─── PRODUCER 1: давач ────────────────────────────────────────────────
func taskSensor(qEvents chan<- Msg) {
    for {
        qEvents <- Msg{MsgSample, analogRead(pinA)} // канал передає КОПІЮ — жодної спільної змінної
        time.Sleep(100 * time.Millisecond)
    }
}

// ─── PRODUCER 2: кнопка (fan-in у ту саму qEvents) ───────────────────
func taskButton(qEvents chan<- Msg) {
    for {
        if digitalRead(pinBtn) == low {
            qEvents <- Msg{MsgButton, 1}
            time.Sleep(50 * time.Millisecond) // debounce
        }
        time.Sleep(10 * time.Millisecond)
    }
}

// ─── CONSUMER + PRODUCER: логіка керування ───────────────────────────
func taskControl(qEvents <-chan Msg, qActuator chan<- Msg) {
    mode := 0 // ← стан ПРИВАТНИЙ всередині ґорутини, не глобальний!
    //            жодного м'ютекса не потрібно
    for m := range qEvents { // спить, поки немає пошти
        switch m.Type {
        case MsgSample:
            if m.Value > 512 {
                qActuator <- Msg{MsgSample, 1}
            }
        case MsgButton:
            mode = (mode + 1) % 3
        case MsgSetMode:
            mode = int(m.Value)
        }
    }
}

// ─── CONSUMER: виконавець на залізі ──────────────────────────────────
func taskActuator(qActuator <-chan Msg) {
    for m := range qActuator {
        // Якщо реле на спільній шині SPI — лише тут беремо м'ютекс на шину
        // busMutex.Lock()
        digitalWrite(pinRelay, m.Value != 0)
        // busMutex.Unlock()
    }
}

// ─── Ініціалізація ────────────────────────────────────────────────────
func main() {
    qEvents := make(chan Msg, 8) // fan-in: Sensor + Button → Control
    qActuator := make(chan Msg, 4) // Control → Actuator

    go taskSensor(qEvents)
    go taskButton(qEvents)
    go taskControl(qEvents, qActuator)
    go taskActuator(qActuator)
    select {} // блокуємось назавжди

    // ЖОДНОЇ спільної змінної між ґорутинами — лише канали.
    // Кожну ґорутину читаємо як окрему просту послідовну програму.
}
