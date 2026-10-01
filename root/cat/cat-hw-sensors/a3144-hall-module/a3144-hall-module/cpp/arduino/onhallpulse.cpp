const uint8_t HALL_PIN = 2;
volatile uint32_t pulse_count = 0;
volatile uint32_t last_time = 0;

void IRAM_ATTR onHallPulse() {
    uint32_t now = micros();
    if (now - last_time > 1000) { // Програмне відсікання завад > 1 кГц
        pulse_count++;
        last_time = now;
    }
}

void setup() {
    pinMode(HALL_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(HALL_PIN), onHallPulse, FALLING);
}
