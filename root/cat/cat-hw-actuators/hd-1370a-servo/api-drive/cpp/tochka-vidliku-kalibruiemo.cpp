#include <Servo.h>

const uint8_t SERVO_PIN = 9;
Servo servo;

void setup() {
    Serial.begin(115200);
    servo.attach(SERVO_PIN);
    servo.writeMicroseconds(1520);      // старт від паспортної нейтралі
    Serial.println(F("Введи ширину в мкс (напр. 1520) і Enter:"));
}

void loop() {
    if (Serial.available()) {
        int us = Serial.parseInt();     // прочитати число
        if (us >= 1000 && us <= 2000) { // не пускати за межі ходу
            servo.writeMicroseconds(us);
            Serial.print(F("-> ")); Serial.print(us); Serial.println(F(" мкс"));
        } else {
            Serial.println(F("поза 1000..2000 — пропущено"));
        }
    }
}
