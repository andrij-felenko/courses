#include <Servo.h>

// Створення об'єкта керування сервоприводом
Servo myServo;

const int SERVO_PIN = 9;
const int MIN_PULSE = 1000; // Мінімальна тривалість імпульсу (0 градусів)
const int MAX_PULSE = 2000; // Максимальна тривалість імпульсу (180 градусів)

void setup() {
    // Прив'язка виводу та конфігурування часових меж імпульсу
    myServo.attach(SERVO_PIN, MIN_PULSE, MAX_PULSE);

    // Установлення вала в нейтральне положення (90 градусів)
    myServo.write(90);
    delay(500);

    // Пряме установлення тривалості імпульсу 1250 мкс (45 градусів)
    myServo.writeMicroseconds(1250);
}

void loop() {
    // Основний цикл вільний для виконання інших завдань
}
