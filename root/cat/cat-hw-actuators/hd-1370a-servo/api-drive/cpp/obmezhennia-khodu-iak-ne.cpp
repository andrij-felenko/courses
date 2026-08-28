#include <Servo.h>

const uint8_t SERVO_PIN = 9;

// --- калібрування конкретного примірника ---
const int NEUTRAL_US = 1520;   // знайдена нейтраль (див. калібрувальний скетч)
const float US_PER_DEG = 11.1; // 1000 мкс на 90° ходу ≈ 11.1 мкс/°

// --- безпечне вікно, підтягнуте ВСЕРЕДИНУ від стопорів ---
const int MIN_US = 1100;       // не 1000: лишаємо запас до стопора
const int MAX_US = 1940;       // не 2000: те саме з іншого боку

Servo servo;

// Затиснути число у [lo, hi] (Arduino має constrain(), але покажемо явно).
int clampInt(int v, int lo, int hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

// Єдина точка входу: кут у градусах від центру -> безпечний імпульс.
void setAngle(float deg) {
    int us = NEUTRAL_US + (int)(deg * US_PER_DEG);
    us = clampInt(us, MIN_US, MAX_US);   // ГОЛОВНИЙ запобіжник
    servo.writeMicroseconds(us);
}

void setup() {
    servo.attach(SERVO_PIN);
    setAngle(0);                 // у центр
}

void loop() {
    setAngle(-30);  delay(800);  // ліворуч
    setAngle(+30);  delay(800);  // праворуч
    setAngle(+90);  delay(800);  // ПРОСИМО забагато — але clamp врятує серво
}
