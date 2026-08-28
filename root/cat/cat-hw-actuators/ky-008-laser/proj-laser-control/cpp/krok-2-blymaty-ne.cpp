const uint8_t  LASER    = 4;
const uint32_t PERIOD   = 500;   // півсекунди на кожен стан (2 Гц миготіння)

uint32_t lastToggle = 0;
bool      beamOn     = false;

void setup() {
    pinMode(LASER, OUTPUT);
    digitalWrite(LASER, LOW);
}

void loop() {
    uint32_t now = millis();
    if (now - lastToggle >= PERIOD) {
        lastToggle = now;
        beamOn = !beamOn;
        digitalWrite(LASER, beamOn ? HIGH : LOW);
    }

    // тут програма вільна робити будь-що інше —
    // блимання йде «саме собою», без пауз
}
