#include <Servo.h>

class ContinuousServo {
private:
    Servo servo;
    int pin;
    int neutralUs; // Індивідуальна нейтраль після калібрування (мкс)
    int deadbandUs; // Напівширина мертвої зони (мкс)

public:
    ContinuousServo(int signalPin, int calibratedNeutralUs = 1500, int deadband = 15)
        : pin(signalPin), neutralUs(calibratedNeutralUs), deadbandUs(deadband) {}

    void attach() {
        servo.attach(pin);
        stop();
    }

    // Speed normalization: -100 (full CCW) to +100 (full CW)
    void setSpeed(int speedPercent) {
        speedPercent = constrain(speedPercent, -100, 100);

        if (abs(speedPercent) == 0) {
            servo.writeMicroseconds(neutralUs);
            return;
        }

        int pulseUs;
        if (speedPercent > 0) {
            pulseUs = neutralUs + deadbandUs + map(speedPercent, 1, 100, 0, 500 - deadbandUs);
        } else {
            pulseUs = neutralUs - deadbandUs - map(-speedPercent, 1, 100, 0, 500 - deadbandUs);
        }

        servo.writeMicroseconds(pulseUs);
    }

    void stop() {
        servo.writeMicroseconds(neutralUs);
    }
};
