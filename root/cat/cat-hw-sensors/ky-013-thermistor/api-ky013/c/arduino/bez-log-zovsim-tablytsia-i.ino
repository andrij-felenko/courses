#include <avr/pgmspace.h>       // тримати таблицю у flash, не в дефіцитній RAM

const uint8_t  PIN_NTC = A0;

// Таблиця «відлік АЦП → температура×10 (десяті °C)», відліки СПАДАЮТЬ
// з нагрівом. °C×10, щоб не втратити десяті на цілій арифметиці.
// Термістор УНИЗУ (між S і −): гарячіше → напруга на S нижча → відлік менший.
struct Point { int16_t adc; int16_t t10; };
const Point TABLE[] PROGMEM = {
  {873, -100}, {834,  -50}, {788,    0}, {738,   50},
  {684,  100}, {627,  150}, {569,  200}, {512,  250},
  {456,  300}, {403,  350}, {354,  400}, {310,  450},
};
const uint8_t N = sizeof(TABLE) / sizeof(TABLE[0]);

void setup() { Serial.begin(9600); }

// відлік → температура×10, лінійна інтерполяція по таблиці (без float!)
int16_t lookupT10(int16_t raw) {
  int16_t a0 = pgm_read_word(&TABLE[0].adc);
  int16_t aN = pgm_read_word(&TABLE[N - 1].adc);
  if (raw >= a0) return pgm_read_word(&TABLE[0].t10);        // за краєм — обрізаємо
  if (raw <= aN) return pgm_read_word(&TABLE[N - 1].t10);

  // знайти сегмент [i, i+1], де adc спадає від >raw до <=raw
  for (uint8_t i = 0; i < N - 1; i++) {
    int16_t aHi = pgm_read_word(&TABLE[i].adc);       // більший відлік
    int16_t aLo = pgm_read_word(&TABLE[i + 1].adc);   // менший відлік
    if (raw <= aHi && raw >= aLo) {
      int16_t tHi = pgm_read_word(&TABLE[i].t10);
      int16_t tLo = pgm_read_word(&TABLE[i + 1].t10);
      // лінійна інтерполяція, уся арифметика ціла (32 біти проти переповнення):
      // t = tHi + (tLo − tHi)·(aHi − raw)/(aHi − aLo)
      int32_t num = (int32_t)(tLo - tHi) * (aHi - raw);
      return tHi + (int16_t)(num / (aHi - aLo));
    }
  }
  return pgm_read_word(&TABLE[N - 1].t10);            // сюди не дійде, для повноти
}

void loop() {
  int16_t raw = analogRead(PIN_NTC);
  int16_t t10 = lookupT10(raw);
  Serial.print(t10 / 10);       // ціла частина градусів
  Serial.print('.');
  Serial.println(abs(t10 % 10)); // десята
  delay(500);
}
