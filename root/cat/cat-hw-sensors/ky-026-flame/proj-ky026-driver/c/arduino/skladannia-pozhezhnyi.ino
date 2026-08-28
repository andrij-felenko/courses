// ── Пожежний робот: наведення на найяскравіше полумʼя двома KY-026 ─────────
// AO лівого давача — A0, правого — A1. DO не використовуємо: тут важить
// ВЕЛИЧИНА жару, а не факт. Мотори — через простий драйвер (напрямок + ШІМ).

const uint8_t AO_L = A0, AO_R = A1;     // аналогові виходи давачів
const uint8_t FAN  = 7;                 // ключ вентилятора-гасія

// Драйвер моторів: піни напрямку + ШІМ-швидкості лівого й правого борту.
const uint8_t L_DIR = 4, L_PWM = 5;
const uint8_t R_DIR = 8, R_PWM = 6;

void drive(int left, int right) {       // швидкості −255..+255 (знак = напрямок)
  digitalWrite(L_DIR, left  >= 0);
  digitalWrite(R_DIR, right >= 0);
  analogWrite(L_PWM, constrain(abs(left),  0, 255));
  analogWrite(R_PWM, constrain(abs(right), 0, 255));
}
