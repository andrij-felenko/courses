// Стан згасання брязкоту для однієї лінії вимикача.
struct Debounced {
    uint8_t pin;             // до якої ніжки під'єднано S
    bool    stable;          // чистий, уже прийнятий рівень
    bool    lastRaw;         // що прочитали минулого разу (для лову зміни)
    uint32_t changedAt;      // коли сире читання востаннє змінилось (millis)
};

const uint16_t DEBOUNCE_MS = 25;   // скільки треба протриматись, щоб повірити

void debounceBegin(Debounced &d, uint8_t pin) {
    d.pin = pin;
    pinMode(pin, INPUT);           // підтяжка вже на платі — свою не вмикаємо
    d.stable = digitalRead(pin);   // початковий стан — те, що зараз на ніжці
    d.lastRaw = d.stable;
    d.changedAt = millis();
}

// Оновити згасання; повертає ЧИСТИЙ рівень ніжки (уже без брязкоту).
bool debounceRead(Debounced &d) {
    bool raw = digitalRead(d.pin);
    if (raw != d.lastRaw) {        // сире читання щойно змінилось —
        d.lastRaw = raw;           //   запам'ятали нове й засікли час,
        d.changedAt = millis();    //   але ПОКИ не віримо йому
    }
    // Якщо нове читання протрималось усю витримку — приймаємо його за правду.
    if (raw != d.stable && (millis() - d.changedAt) >= DEBOUNCE_MS) {
        d.stable = raw;
    }
    return d.stable;
}
