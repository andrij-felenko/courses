const uint8_t TRIG_PIN = 9;
const uint8_t ECHO_PIN = 10;

// Тайм-аут очікування луни, мкс. Апаратно модуль сам гасить ECHO
// приблизно за 38000 мкс; беремо трохи більше, щоб не обрізати дальні цілі.
const unsigned long ECHO_TIMEOUT_US = 40000UL;

void setup() {
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    digitalWrite(TRIG_PIN, LOW);
    Serial.begin(9600);
}

// Повертає відстань у см, або 0 — якщо луни не було (порожньо / поза межами).
unsigned int measureCm() {
    // Такт 1: чистий поштовх 10 мкс. Спершу тягнемо в 0 на 2 мкс,
    // щоб фронт був різкий і без залишкового «дзвону» від попереднього разу.
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    // Такти 2–3: ширина високого рівня на ECHO = час польоту t, мкс.
    unsigned long t = pulseIn(ECHO_PIN, HIGH, ECHO_TIMEOUT_US);

    if (t == 0) return 0;          // луни не почули — не плутати з «0 см»!
    return (unsigned int)(t / 58); // Такт 4: мкс → см
}

void loop() {
    unsigned int cm = measureCm();
    if (cm == 0) {
        Serial.println(F("out of range"));
    } else {
        Serial.print(cm);
        Serial.println(F(" cm"));
    }
    delay(60);                     // пауза між вимірами ≥ 60 мс
}
