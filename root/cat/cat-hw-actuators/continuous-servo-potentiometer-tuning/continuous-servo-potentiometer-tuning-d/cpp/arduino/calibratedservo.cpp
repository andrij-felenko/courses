#include <Arduino.h>
#include <Servo.h>

// Клас для керування сервоприводом з компенсацією offset та deadband
class CalibratedServo {
private:
    Servo servo;
    int pin;
    int neutralOffsetUs;
    int deadbandUs;

public:
    CalibratedServo(int servoPin, int offsetUs = 0, int deadbandWidthUs = 10)
        : pin(servoPin), neutralOffsetUs(offsetUs), deadbandUs(deadbandWidthUs) {}

    void attach() {
        servo.attach(pin);
    }

    void writeMicrosecondsCalibrated(int targetPulseUs) {
        int effectiveNeutral = 1500 + neutralOffsetUs;
        int delta = targetPulseUs - 1500;

        // Зона нечутливості фіксує вал у точній програмній нейтралі
        if (abs(delta) <= deadbandUs) {
            servo.writeMicroseconds(effectiveNeutral);
        } else {
            // Зсув застосовується до всього робочого діапазону
            servo.writeMicroseconds(targetPulseUs + neutralOffsetUs);
        }
    }
};

CalibratedServo myServo(9, 35, 8); // Пін 9, offset +35 мкс, deadband ±8 мкс

void setup() {
    myServo.attach();
}

void loop() {
    // Вхідний сигнал 1500 мкс видає 1535 мкс на привод, гарантуючи зупинку
    myServo.writeMicrosecondsCalibrated(1500);
    delay(1000);
}
