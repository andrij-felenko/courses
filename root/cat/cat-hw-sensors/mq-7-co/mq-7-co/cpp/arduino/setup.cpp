const uint8_t HEATER_PIN = 9;
const uint8_t SENSOR_PIN = A0;

enum HeaterPhase { PHASE_HIGH_5V, PHASE_LOW_1V4 };
HeaterPhase currentPhase = PHASE_HIGH_5V;
unsigned long lastPhaseSwitchMs = 0;
bool sampleTaken = false;

void setup() {
    pinMode(HEATER_PIN, OUTPUT);
    analogWrite(HEATER_PIN, 255); // 5.0 V нагрів
    lastPhaseSwitchMs = millis();
}

void loop() {
    unsigned long currentMs = millis();

    if (currentPhase == PHASE_HIGH_5V) {
        if (currentMs - lastPhaseSwitchMs >= 60000UL) { // 60 с при 5 В
            currentPhase = PHASE_LOW_1V4;
            analogWrite(HEATER_PIN, 71); // ~1.4 V (PWM 71/255)
            lastPhaseSwitchMs = currentMs;
            sampleTaken = false;
        }
    } else if (currentPhase == PHASE_LOW_1V4) {
        // Зчитування на 85-й секунді
        if (!sampleTaken && (currentMs - lastPhaseSwitchMs >= 85000UL)) {
            int rawAdc = analogRead(SENSOR_PIN);
            // Обробка сигналу
            sampleTaken = true;
        }

        if (currentMs - lastPhaseSwitchMs >= 90000UL) { // 90 с при 1.4 В
            currentPhase = PHASE_HIGH_5V;
            analogWrite(HEATER_PIN, 255); // Повернення до 5.0 V
            lastPhaseSwitchMs = currentMs;
        }
    }
}
