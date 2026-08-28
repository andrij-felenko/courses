// 4 розряди: 8 сегментних ліній спільні, 4 «цифрові» вибирають розряд.
const uint8_t SEG[8]   = { 2, 3, 4, 5, 6, 7, 8, 9 };   // a..g,DP (спільні!)
const uint8_t DIGIT[4] = { 10, 11, 12, 13 };           // катоди 4 розрядів

uint8_t frame[4] = { 0, 0, 0, 0 };   // що показувати в кожному розряді (маски)

void setup() {
  for (uint8_t i = 0; i < 8; i++) pinMode(SEG[i], OUTPUT);
  for (uint8_t d = 0; d < 4; d++) { pinMode(DIGIT[d], OUTPUT);
                                    digitalWrite(DIGIT[d], HIGH); } // усі згашені
}

// Один прохід: швидко «промалювати» всі 4 розряди по черзі.
void multiplex() {
  for (uint8_t d = 0; d < 4; d++) {
    // 1) згасити все, щоб не було «привидів» від попереднього розряду
    for (uint8_t i = 0; i < 4; i++) digitalWrite(DIGIT[i], HIGH);
    // 2) виставити маску поточного розряду на спільні сегменти
    uint8_t m = frame[d];
    for (uint8_t i = 0; i < 8; i++) digitalWrite(SEG[i], (m >> i) & 1);
    // 3) увімкнути ЛИШЕ цей розряд (катод на землю)
    digitalWrite(DIGIT[d], LOW);
    delayMicroseconds(2000);          // ~2 мс на розряд → ~125 Гц на всі 4
  }
}

void setNumber(int n) {              // розкласти число на 4 цифри
  for (int d = 3; d >= 0; d--) { frame[d] = FONT[n % 10]; n /= 10; }
}

void loop() {
  setNumber(1234);
  multiplex();                        // кликати безперервно
}
