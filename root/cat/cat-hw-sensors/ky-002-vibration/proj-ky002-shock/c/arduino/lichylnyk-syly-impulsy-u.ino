const uint8_t PIN_SHOCK = 2;
const uint32_t WINDOW_MS   = 100;   // вікно вимірювання сили
const uint32_t STRONG_HITS = 12;    // поріг «сильний струс» (імпульсів за вікно)

volatile uint32_t g_hits = 0;       // фронти в поточному вікні (нарощує ISR)

uint32_t g_windowStart = 0;

void onHit() { g_hits++; }          // максимально коротка ISR

void setup() {
    pinMode(PIN_SHOCK, INPUT_PULLUP);
    Serial.begin(9600);
    delay(50);
    int idle = digitalRead(PIN_SHOCK);
    attachInterrupt(digitalPinToInterrupt(PIN_SHOCK),
                    onHit, idle == HIGH ? FALLING : RISING);
    g_windowStart = millis();
}

void loop() {
    if (millis() - g_windowStart >= WINDOW_MS) {
        // Забрати й обнулити лічильник вікна атомарно.
        noInterrupts();
        uint32_t hits = g_hits;
        g_hits = 0;
        interrupts();
        g_windowStart += WINDOW_MS;

        if (hits == 0) {
            // тиша — нічого не друкуємо, щоб не засмічувати монітор
        } else if (hits >= STRONG_HITS) {
            Serial.print("СИЛЬНИЙ струс: ");
            Serial.print(hits);
            Serial.println(" імпульсів");
        } else {
            Serial.print("легкий струс: ");
            Serial.print(hits);
            Serial.println(" імпульсів");
        }
    }
    // головний цикл вільний
}
