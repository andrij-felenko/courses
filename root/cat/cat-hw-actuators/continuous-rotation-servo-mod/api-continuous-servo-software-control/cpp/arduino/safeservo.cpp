class SafeServo {
private:
    Servo servoDevice;
    int pinNumber;
    unsigned long lastCommandMs;
    unsigned long timeoutMs;
    bool isAttached;

public:
    SafeServo(int pin, unsigned long timeout = 500)
        : pinNumber(pin), lastCommandMs(0), timeoutMs(timeout), isAttached(false) {}

    void setSpeed(uint16_t pulseUs) {
        if (!isAttached) {
            servoDevice.attach(pinNumber);
            isAttached = true;
        }
        servoDevice.writeMicroseconds(pulseUs);
        lastCommandMs = millis();
    }

    // Регулярно викликається у циклі для перевірки наявності зв'язку
    void checkWatchdog() {
        if (isAttached && (millis() - lastCommandMs > timeoutMs)) {
            servoDevice.detach(); // Аварійне вимкнення генерації ШІМ
            isAttached = false;
        }
    }
};
