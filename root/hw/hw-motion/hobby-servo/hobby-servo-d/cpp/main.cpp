// Спосіб «у лоб»: delayMicroseconds() і digitalWrite() як в Arduino.
#include <Arduino.h>

const int SERVO_PIN = 9;
const int FRAME_US  = 20000;   // період кадру, 20 мс = 50 Гц

// один імпульс заданої ширини + добивання кадру до 20 мс
void servoPulse(int pin, int width_us) {
    digitalWrite(pin, HIGH);
    delayMicroseconds(width_us);          // ширина = кут
    digitalWrite(pin, LOW);
    delayMicroseconds(FRAME_US - width_us);  // решта кадру — пауза
}

void setup() {
    pinMode(SERVO_PIN, OUTPUT);
}

void loop() {
    servoPulse(SERVO_PIN, 1500);   // 1500 мкс → нейтраль (центр)
}
