const uint8_t TILT = 2;                 // на AVR переривання лише D2 і D3
const unsigned long SETTLE = 30;

volatile bool pinChanged = false;       // прапорець з ISR — ОБОВ'ЯЗКОВО volatile
unsigned long lastChangeMs = 0;
bool lastRaw = HIGH, stableState = HIGH;
unsigned long tiltCount = 0;

void onEdge() {                          // ISR — коротка, як постріл
    pinChanged = true;                   // жодного Serial, digitalRead-логіки, delay тут!
}

void setup() {
    pinMode(TILT, INPUT_PULLUP);
    Serial.begin(9600);
    lastRaw = stableState = digitalRead(TILT);
    attachInterrupt(digitalPinToInterrupt(TILT), onEdge, CHANGE);  // на будь-який фронт
}

void loop() {
    if (pinChanged) {                    // ISR щось помітила
        pinChanged = false;
        bool raw = digitalRead(TILT);
        if (raw != lastRaw) { lastChangeMs = millis(); lastRaw = raw; }
    }
    // гасіння крутиться в циклі, спокійно
    if ((millis() - lastChangeMs) > SETTLE && lastRaw != stableState) {
        stableState = lastRaw;
        if (stableState == LOW) {
            tiltCount++;
            Serial.print("нахилів: "); Serial.println(tiltCount);
        }
    }
}
