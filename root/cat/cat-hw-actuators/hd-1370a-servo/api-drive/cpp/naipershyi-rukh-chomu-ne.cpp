#include <Servo.h>

const uint8_t SERVO_PIN = 9;   // сигнальний (жовтий) дріт на ~D9
Servo servo;                   // об'єкт-керувач одним серво

void setup() {
    servo.attach(SERVO_PIN);   // почепити пін; бібліотека сама пускає 50 Гц
    servo.writeMicroseconds(1520);  // справжня нейтраль HD-1370A
    delay(500);
}

void loop() {
    servo.writeMicroseconds(1520);  // центр
    delay(1000);
    servo.writeMicroseconds(1520 + 333);  // ≈ +30° від центру (30° · 11.1 мкс/°)
    delay(1000);
}
