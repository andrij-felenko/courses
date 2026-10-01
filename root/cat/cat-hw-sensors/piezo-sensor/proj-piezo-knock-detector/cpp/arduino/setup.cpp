const int SENSOR_PIN = A0;
const int NOISE_THRESHOLD = 50;
const unsigned long DEAD_TIME_MS = 80;

unsigned long lastKnockTime = 0;

void setup() {
    Serial.begin(115200);
}

void loop() {
    unsigned long now = millis();
    int rawValue = analogRead(SENSOR_PIN);

    if (now - lastKnockTime < DEAD_TIME_MS) {
        return;
    }

    if (rawValue > NOISE_THRESHOLD) {
        lastKnockTime = now;
        processKnock(rawValue);
    }
}
