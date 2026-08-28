// Керування кроковим драйвером через два піни STEP/DIR.
#define PIN_STEP  4
#define PIN_DIR   5

void step_pulse(void) {              // один імпульс = один крок
    digitalWrite(PIN_STEP, HIGH);
    delayMicroseconds(3);            // коротка «полиця» — драйвер ловить фронт
    digitalWrite(PIN_STEP, LOW);
    delayMicroseconds(3);
}

void move_steps(int n, int forward) {
    digitalWrite(PIN_DIR, forward ? HIGH : LOW);   // напрямок читання таблиці
    for (int i = 0; i < n; i++) {
        step_pulse();
        delayMicroseconds(1200);     // пауза між кроками задає швидкість
    }
}

void quarter_turn(void) {
    move_steps(200 / 4, 1);          // 50 кроків уперед = 90°
}
