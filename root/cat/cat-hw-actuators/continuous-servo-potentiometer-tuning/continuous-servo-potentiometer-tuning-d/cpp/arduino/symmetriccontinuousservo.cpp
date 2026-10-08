#include <Arduino.h>
#include <Servo.h>

class SymmetricContinuousServo {
private:
    Servo servo;
    int pin;
    int neutralUs;
    int deadbandUs;
    int minRevUs;
    int maxFwdUs;

public:
    SymmetricContinuousServo(int servoPin, int neutral = 1500, int deadband = 8, int minRev = 1050, int maxFwd = 1950)
        : pin(servoPin), neutralUs(neutral), deadbandUs(deadband), minRevUs(minRev), maxFwdUs(maxFwd) {}

    void attach() {
        servo.attach(pin);
    }

    // Вхідне значення speedNorm в діапазоні від -1.0 (макс назад) до +1.0 (макс вперед)
    void setSpeedNormalized(float speedNorm) {
        speedNorm = constrain(speedNorm, -1.0f, 1.0f);
        int outputUs = neutralUs;

        if (speedNorm > 0.001f) {
            int activeStart = neutralUs + deadbandUs;
            outputUs = activeStart + (int)(speedNorm * (maxFwdUs - activeStart));
        } else if (speedNorm < -0.001f) {
            int activeStart = neutralUs - deadbandUs;
            outputUs = activeStart + (int)(speedNorm * (activeStart - minRevUs));
        } else {
            outputUs = neutralUs;
        }

        servo.writeMicroseconds(outputUs);
    }
};

SymmetricContinuousServo driveWheel(9, 1535, 8, 1060, 1920);

void setup() {
    driveWheel.attach();
}

void loop() {
    // Одинакова кутова швидкість вперед та назад
    driveWheel.setSpeedNormalized(0.5f);
    delay(2000);
    driveWheel.setSpeedNormalized(0.0f); // Надійна зупинка
    delay(1000);
    driveWheel.setSpeedNormalized(-0.5f);
    delay(2000);
    driveWheel.setSpeedNormalized(0.0f);
    delay(1000);
}
