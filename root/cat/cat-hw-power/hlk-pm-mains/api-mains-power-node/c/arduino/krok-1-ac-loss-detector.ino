/* ============================================================================
   krok-1-ac-loss-detector.ino — Arduino: моніторинг наявності мережі 220 В
   ========================================================================== */

const uint8_t PIN_ZERO_CROSS = 2;    // Пін із перериванням (оптопара PC814)
const uint8_t PIN_LED_STATUS = 13;   // Індикатор стану мережі

volatile unsigned long lastPulseTimeMicros = 0;
volatile bool acPresent = false;

void IRAM_ATTR onZeroCross() {
    lastPulseTimeMicros = micros();
    acPresent = true;
}

void setup() {
    Serial.begin(115200);
    pinMode(PIN_ZERO_CROSS, INPUT_PULLUP);
    pinMode(PIN_LED_STATUS, OUTPUT);

    attachInterrupt(digitalPinToInterrupt(PIN_ZERO_CROSS), onZeroCross, FALLING);
    lastPulseTimeMicros = micros();
    Serial.println(F("HLK-PM Mains Detector: Ініціалізовано"));
}

void loop() {
    unsigned long now = micros();
    // При 50 Гц імпульси йдуть кожні 10 000 мкс. Якщо пауза > 15 000 мкс — мережа зникла!
    if ((now - lastPulseTimeMicros) > 15000) {
        acPresent = false;
    }

    if (acPresent) {
        digitalWrite(PIN_LED_STATUS, HIGH);
    } else {
        digitalWrite(PIN_LED_STATUS, LOW);
        Serial.println(F("УВАГА: Мережу 220 В знеструмлено!"));
        delay(100);
    }
}
