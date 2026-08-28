const uint8_t KNOCK = 4;              // вивід S — на GPIO4 (на ESP32 годиться майже будь-який)
const uint8_t LED   = 2;              // вбудований світлодіод багатьох DevKit
const unsigned long LOCKOUT = 60;     // глухе вікно, мс

volatile bool     knockFlag = false;  // спільний з обробником — обов'язково volatile
volatile uint32_t knockAt   = 0;      // мітка часу; на ESP32 millis() в ISR працює

// IRAM_ATTR — покласти обробник у швидку внутрішню RAM (обов'язково, надто з Wi-Fi)
void IRAM_ATTR onKnock() {
    knockFlag = true;
    knockAt   = millis();             // на ESP32 годинник в ISR іде — можна мітити тут
}

unsigned long lastKnock = 0;
unsigned long count     = 0;

void setup() {
    pinMode(KNOCK, INPUT_PULLUP);
    pinMode(LED, OUTPUT);
    Serial.begin(115200);
    attachInterrupt(digitalPinToInterrupt(KNOCK), onKnock, FALLING);
}

void loop() {
    if (knockFlag) {
        knockFlag = false;
        uint32_t t = knockAt;         // читаємо мітку, поставлену обробником
        if (t - lastKnock > LOCKOUT) {
            lastKnock = t;
            count++;
            digitalWrite(LED, HIGH);
            Serial.printf("стук #%lu\n", count);
        }
    }
    if (millis() - lastKnock > 30) digitalWrite(LED, LOW);
}
