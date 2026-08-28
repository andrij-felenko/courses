// ESP32: живлення давача — 3.3 В! Сигнал S — на звичайну ногу з підтяжкою.
const uint8_t TILT = 14;               // звичайний GPIO (НЕ 34–39): має INPUT_PULLUP
const unsigned long SETTLE = 30;

volatile bool pinChanged = false;      // спільна з ISR → volatile
unsigned long lastChangeMs = 0;
bool lastRaw = HIGH, stableState = HIGH;
unsigned long tiltCount = 0;

void IRAM_ATTR onEdge() {              // на ESP32 ISR — обов'язково IRAM_ATTR
    pinChanged = true;                 // лише прапорець, нічого важкого
}

void setup() {
    pinMode(TILT, INPUT_PULLUP);       // на GPIO14 підтяжка є; на 34–39 її НЕ буде
    Serial.begin(115200);
    lastRaw = stableState = digitalRead(TILT);
    attachInterrupt(digitalPinToInterrupt(TILT), onEdge, CHANGE);
}

void loop() {
    if (pinChanged) {
        pinChanged = false;
        bool raw = digitalRead(TILT);
        if (raw != lastRaw) { lastChangeMs = millis(); lastRaw = raw; }
    }
    if ((millis() - lastChangeMs) > SETTLE && lastRaw != stableState) {
        stableState = lastRaw;
        if (stableState == LOW) {
            tiltCount++;
            Serial.print("нахилів: "); Serial.println(tiltCount);
        }
    }
}
