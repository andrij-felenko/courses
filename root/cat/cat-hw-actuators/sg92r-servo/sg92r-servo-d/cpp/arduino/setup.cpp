// Безпечне керування сервоприводом SG92R з обмеженням імпульсу
#include <ESP32Servo.h>

Servo myServo;
const int SERVO_PIN = 18;
const int SAFE_MIN_PULSE_US = 540;  // Апаратно виміряний мінімум (мкс)
const int SAFE_MAX_PULSE_US = 2400; // Апаратно виміряний максимум (мкс)

void setup() {
    myServo.setPeriodHertz(50); // Стандартна частота 50 Гц
    myServo.attach(SERVO_PIN, SAFE_MIN_PULSE_US, SAFE_MAX_PULSE_US);
}

void writeSafeAngle(int targetAngle) {
    // Жорстке обмеження кута у програмному діапазоні 0..180 градусів
    int clampedAngle = constrain(targetAngle, 0, 180);
    myServo.write(clampedAngle);
}
