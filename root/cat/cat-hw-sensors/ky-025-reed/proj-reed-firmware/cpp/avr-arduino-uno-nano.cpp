const uint8_t REED = 2;          // D0 — ОБОВ'ЯЗКОВО на D2 або D3 (тільки там переривання)
const uint8_t LED  = 13;

const uint32_t DEBOUNCE_MS = 30; // мертве вікно проти брязкоту, тепер — усередині ISR

volatile uint32_t counter    = 0;   // лічильник змінює переривання → volatile
volatile uint32_t t_last_isr = 0;   // мить останньої прийнятої події

// ISR: якнайкоротша. Лише гасимо брязкіт вікном і нарощуємо лічильник.
void on_reed() {
    uint32_t now = millis();
    if (now - t_last_isr >= DEBOUNCE_MS) {   // усе, що ближче за DEBOUNCE_MS — брязкіт
        t_last_isr = now;
        counter++;
    }
}

void setup() {
    pinMode(REED, INPUT);
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
    // Магніт дає спад D0 (активний LOW) → ловимо FALLING:
    attachInterrupt(digitalPinToInterrupt(REED), on_reed, FALLING);
    Serial.println("Переривання на герконі увімкнено.");
}

uint32_t shown = 0;

void loop() {
    // Основний код вільний робити будь-що; лічильник росте «сам».
    if (counter != shown) {
        shown = counter;
        Serial.print("подій: ");
        Serial.println(shown);
        digitalWrite(LED, HIGH); delay(15); digitalWrite(LED, LOW);   // коротке блимання
    }
    // ... тут може бути будь-яка інша важка робота — переривання її не пропустить ...
}
