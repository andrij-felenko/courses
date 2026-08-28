// ── Керування сервами на UBEC-шині. Arduino (Uno/Nano, ATmega328) ──
// Бібліотека Servo сама генерує 50-Гц сигнал через апаратний таймер.
// Команду задаємо в МІКРОСЕКУНДАХ ширини — чесніше за градуси.
#include <Servo.h>

const uint8_t  N = 4;                 // скільки серв на шині
const uint8_t  PIN[N] = {3, 5, 6, 9}; // сигнальні ніжки (будь-які цифрові)
Servo servo[N];

const uint16_t US_MIN = 1000;         // край ходу, мкс (звірити з паспортом!)
const uint16_t US_MID = 1500;         // центр
const uint16_t US_MAX = 2000;         // інший край

// градуси 0..180 → мікросекунди 1000..2000 (лінійно)
uint16_t angleToUs(uint8_t deg) {
  if (deg > 180) deg = 180;
  return US_MIN + (uint32_t)(US_MAX - US_MIN) * deg / 180;
}

void setup() {
  for (uint8_t i = 0; i < N; i++) {
    servo[i].attach(PIN[i]);          // таймер починає гнати сигнал
    servo[i].writeMicroseconds(US_MID); // старт із центру — безпечний кут
  }
}

// Повернути одне серво в кут. Ширину пише таймер, ми лише задаємо число.
void moveServo(uint8_t i, uint8_t deg) {
  servo[i].writeMicroseconds(angleToUs(deg));
}

void loop() {
  moveServo(0, 45);   // приклад: розкидати серва по кутах
  moveServo(1, 135);
  delay(1000);
}
