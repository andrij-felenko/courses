#include <Arduino.h>

const uint8_t PIN_DOUT  = 3;   // DOUT  від HX711  → вхід MCU
const uint8_t PIN_SCK   = 2;   // PD_SCK від MCU   → вхід HX711

// Зайві такти задають режим на НАСТУПНИЙ відлік:
//   1 → канал A, підсилення 128;  2 → канал B, 32;  3 → канал A, 64
const uint8_t EXTRA_PULSES = 1;        // канал A, ×128 — звичні ваги

bool hx711_ready() {
    return digitalRead(PIN_DOUT) == LOW;   // DOUT↓ = дані готові
}

// Зчитати один відлік. Повертає 24-бітне знакове число,
// розширене до int32_t (доповняльний код збережено).
int32_t hx711_read() {
    while (!hx711_ready()) { /* чекаємо спаду DOUT */ }

    uint32_t value = 0;
    for (uint8_t i = 0; i < 24; i++) {     // 24 біти, старший перший
        digitalWrite(PIN_SCK, HIGH);
        delayMicroseconds(1);
        value = (value << 1) | digitalRead(PIN_DOUT);
        digitalWrite(PIN_SCK, LOW);
        delayMicroseconds(1);
    }

    for (uint8_t i = 0; i < EXTRA_PULSES; i++) {   // вибір каналу/підсилення
        digitalWrite(PIN_SCK, HIGH);
        delayMicroseconds(1);
        digitalWrite(PIN_SCK, LOW);
        delayMicroseconds(1);
    }

    // розширення знаку: біт 23 — знаковий у доповняльному коді
    if (value & 0x800000UL)
        value |= 0xFF000000UL;

    return (int32_t)value;
}

void setup() {
    pinMode(PIN_SCK, OUTPUT);
    pinMode(PIN_DOUT, INPUT);
    digitalWrite(PIN_SCK, LOW);     // низький рівень — мікросхема не спить
    Serial.begin(115200);
    hx711_read();                   // холостий зчит: відкинути перший брудний відлік
}

void loop() {
    int32_t raw = hx711_read();     // сирий код, від −8388608 до +8388607
    Serial.println(raw);
    delay(100);
}
