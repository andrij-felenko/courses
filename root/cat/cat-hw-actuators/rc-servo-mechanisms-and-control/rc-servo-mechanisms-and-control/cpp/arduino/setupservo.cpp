// Позиціонування сервоприводу у C++ (Arduino Framework)
#include <Arduino.h>
#include <Servo.h>

Servo myServo;
const int SERVO_PIN = 9;

void setupServo() {
    myServo.attach(SERVO_PIN, 1000, 2000);
}

void setServoAngle(int angleDegrees) {
    if (angleDegrees >= 0 && angleDegrees <= 180) {
        myServo.write(angleDegrees);
    }
}
