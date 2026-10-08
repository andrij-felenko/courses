class RampedServo {
private:
    Servo servoDevice;
    uint16_t currentUs;
    uint16_t targetUs;
    uint16_t stepUs;
    unsigned long lastUpdateMs;
    uint16_t updateIntervalMs;

public:
    RampedServo(uint16_t initialUs = 1500, uint16_t step = 5, uint16_t interval = 20)
        : currentUs(initialUs), targetUs(initialUs), stepUs(step), 
          lastUpdateMs(0), updateIntervalMs(interval) {}

    void setTargetPulse(uint16_t target) {
        targetUs = target;
    }

    // Неблокуючий метод, який викликається у головному циклі loop()
    void update() {
        unsigned long now = millis();
        if (now - lastUpdateMs >= updateIntervalMs) {
            lastUpdateMs = now;

            if (currentUs < targetUs) {
                currentUs += stepUs;
                if (currentUs > targetUs) currentUs = targetUs;
            } else if (currentUs > targetUs) {
                currentUs -= stepUs;
                if (currentUs < targetUs) currentUs = targetUs;
            }

            servoDevice.writeMicroseconds(currentUs);
        }
    }
};
