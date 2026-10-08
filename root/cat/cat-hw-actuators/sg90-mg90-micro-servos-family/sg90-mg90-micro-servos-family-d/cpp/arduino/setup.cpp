#include <ESP32Servo.h>

Servo microServo;

// Ініціалізація керування сервоприводом з точними межами імпульсу
void setup() {
    // Прив'язка до піна з межами імпульсу: 500 мкс (0 градусів) - 2400 мкс (180 градусів)
    // Стандартна частота кадрів становить 50 Гц (20 мс)
    microServo.setPeriodHertz(50);
    microServo.attach(18, 500, 2400);
    
    // Встановлення початкового нейтрального кута 90 градусів
    microServo.write(90);
}

void loop() {
    // Плавне переміщення вала для запобігання брязкання (jitter)
    for (int angle = 0; angle <= 180; angle += 5) {
        microServo.write(angle);
        delay(30);
    }
    for (int angle = 180; angle >= 0; angle -= 5) {
        microServo.write(angle);
        delay(30);
    }
}
