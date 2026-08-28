#include <Servo.h>

const uint8_t SERVO_PIN = 9;
const int   NEUTRAL_US = 1520;
const float US_PER_DEG = 11.1;
const int   MIN_US = 1100, MAX_US = 1940;
const unsigned long FRAME_MS = 20;   // крок часу = кадр серва (50 Гц)

Servo servo;
float curDeg = 0;      // де вал зараз (у градусах від центру)
float tgtDeg = 0;      // куди хочемо
float stepDeg = 1.0;   // приріст на кадр -> задає швидкість
unsigned long lastFrame = 0;

int clampInt(int v, int lo, int hi) { return v < lo ? lo : v > hi ? hi : v; }

void applyDeg(float deg) {
    int us = clampInt(NEUTRAL_US + (int)(deg * US_PER_DEG), MIN_US, MAX_US);
    servo.writeMicroseconds(us);
}

// Викликати часто; сама рухає не частіше, ніж раз на кадр.
void serviceMove() {
    unsigned long now = millis();
    if (now - lastFrame < FRAME_MS) return;   // ще не час на новий крок
    lastFrame = now;

    float diff = tgtDeg - curDeg;
    if (fabs(diff) <= stepDeg) curDeg = tgtDeg;         // дійшли — сісти точно на ціль
    else curDeg += (diff > 0 ? stepDeg : -stepDeg);     // крок у бік цілі
    applyDeg(curDeg);
}

void moveTo(float deg) { tgtDeg = deg; }   // лише задати ціль, рух зробить serviceMove

void setup() {
    servo.attach(SERVO_PIN);
    applyDeg(0);
}

void loop() {
    // приклад: гойдати між −30 і +30, міняючи ціль по досягненні
    if (curDeg == tgtDeg) {
        moveTo(tgtDeg <= 0 ? +30 : -30);
    }
    serviceMove();     // саме тут відбувається плавний крок
    // ... тут loop() вільний робити будь-що інше ...
}
