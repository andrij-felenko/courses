// Реле-модуль на ніжці; ТИПОВИЙ модуль — active-low (LOW = увімкнено).
const uint8_t PIN_RELAY = 7;

// Явні імена станів, щоб у коді не думати щоразу про інверсію.
const uint8_t RELAY_ON  = LOW;    // active-low: нуль вмикає
const uint8_t RELAY_OFF = HIGH;   // одиниця вимикає

void setup() {
    // 1) СПЕРШУ виставити безпечний (вимкнений) рівень на ніжку.
    digitalWrite(PIN_RELAY, RELAY_OFF);
    // 2) ТІЛЬКИ ТЕПЕР зробити ніжку виходом — вона вже тримає OFF.
    pinMode(PIN_RELAY, OUTPUT);
    // Тепер реле гарантовано вимкнене, старт тихий.
}

void loop() {
}
