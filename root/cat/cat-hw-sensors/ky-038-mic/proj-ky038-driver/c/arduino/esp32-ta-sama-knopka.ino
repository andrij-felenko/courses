const uint8_t PIN_DO = 4;          // будь-який вільний GPIO на ESP32
volatile unsigned long soundCount = 0;
volatile unsigned long lastEventISR = 0;
const unsigned long WINDOW_MS = 300;
portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;   // для атомарності на 2 ядрах

void IRAM_ATTR onSound() {         // ISR у внутрішній RAM
    unsigned long now = millis();
    portENTER_CRITICAL_ISR(&mux);
    if (now - lastEventISR > WINDOW_MS) {
        lastEventISR = now;
        soundCount++;
    }
    portEXIT_CRITICAL_ISR(&mux);
}

void setup() {
    pinMode(PIN_DO, INPUT);
    Serial.begin(115200);
    delay(300);
    attachInterrupt(PIN_DO, onSound, RISING);   // на ESP32 pin передають напряму
}

void loop() {
    static unsigned long shown = 0;
    portENTER_CRITICAL(&mux);
    unsigned long c = soundCount;
    portEXIT_CRITICAL(&mux);
    if (c != shown) { shown = c; Serial.printf("подій: %lu\n", c); }
    delay(20);
}
