// Прецизійне налаштування апаратного таймера для сервоприводів у C++ (Arduino Framework)
#include <Arduino.h>
#include <ESP32Servo.h>

Servo servoMotor;

void setupHardwareServo() {
    // Використання апаратного таймера для генерації ШІМ-кадру 50 Гц без фазового дрижання
    ESP32PWM::allocateTimer(0);
    servoMotor.setPeriodHertz(50); // Фіксована частота кадрів 50 Гц (T_frame = 20 мс)
    
    // Підключення виводу з межами ширини імпульсу 1000–2000 мкс
    servoMotor.attach(18, 1000, 2000);
    
    // Встановлення кута нейтралі (1500 мкс)
    servoMotor.writeMicroseconds(1500);
}
