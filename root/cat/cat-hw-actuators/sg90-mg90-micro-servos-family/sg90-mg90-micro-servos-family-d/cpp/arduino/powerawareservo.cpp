#include <ESP32Servo.h>

class PowerAwareServo {
private:
    Servo servo;
    int currentPulseUs;

public:
    void attachPin(int pin) {
        servo.setPeriodHertz(50);
        servo.attach(pin, 500, 2400);
        currentPulseUs = 1500;
        servo.writeMicroseconds(currentPulseUs);
    }

    // Обмеження швидкості зміни кута для зниження пускового струму
    void moveToMicrosecondsSmooth(int targetPulseUs, int stepUs = 15, int stepDelayMs = 10) {
        if (targetPulseUs > currentPulseUs) {
            for (int p = currentPulseUs; p <= targetPulseUs; p += stepUs) {
                servo.writeMicroseconds(p);
                delay(stepDelayMs);
            }
        } else {
            for (int p = currentPulseUs; p >= targetPulseUs; p -= stepUs) {
                servo.writeMicroseconds(p);
                delay(stepDelayMs);
            }
        }
        currentPulseUs = targetPulseUs;
        servo.writeMicroseconds(currentPulseUs);
    }
};
