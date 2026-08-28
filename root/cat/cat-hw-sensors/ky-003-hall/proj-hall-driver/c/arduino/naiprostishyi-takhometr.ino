const uint8_t HALL = 2;          // S давача KY-003 → D2 (лінія переривання на Uno)

volatile uint32_t pulses = 0;    // лічильник, який чіпає ISR — ОБОВʼЯЗКОВО volatile

void onPulse() {                 // ISR: якнайкоротша
    pulses++;
}

void setup() {
    pinMode(HALL, INPUT_PULLUP); // відкритий колектор → внутрішня підтяжка обовʼязкова
    Serial.begin(115200);
    attachInterrupt(digitalPinToInterrupt(HALL), onPulse, FALLING);
}

const uint32_t WINDOW_MS = 250;  // вікно вимірювання
uint32_t windowStart = 0;

void loop() {
    if (millis() - windowStart >= WINDOW_MS) {
        // атомарно зчитуємо й обнуляємо лічильник (див. пояснення нижче)
        noInterrupts();
        uint32_t n = pulses;
        pulses = 0;
        interrupts();
        windowStart += WINDOW_MS;

        // n імпульсів за WINDOW_MS мілісекунд; магніт один → n обертів за вікно
        float rpm = (float)n * (60000.0 / WINDOW_MS);
        Serial.print("RPM: ");
        Serial.println(rpm, 0);
    }
    // тут головний цикл вільний робити будь-що — імпульси не губляться
}
