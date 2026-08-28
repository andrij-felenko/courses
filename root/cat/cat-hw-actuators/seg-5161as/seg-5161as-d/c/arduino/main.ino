// Виводи МК під сегменти a,b,c,d,e,f,g,DP (спільний катод: HIGH = світиться)
const uint8_t SEG_PIN[8] = { 2, 3, 4, 5, 6, 7, 8, 9 };  // a b c d e f g DP

// Маски цифр 0..9. Біт 0 = a, біт 1 = b, ... біт 6 = g, біт 7 = DP.
const uint8_t DIGIT[10] = {
  0b00111111, // 0 -> a b c d e f
  0b00000110, // 1 -> b c
  0b01011011, // 2 -> a b d e g
  0b01001111, // 3 -> a b c d g
  0b01100110, // 4 -> b c f g
  0b01101101, // 5 -> a c d f g
  0b01111101, // 6 -> a c d e f g
  0b00000111, // 7 -> a b c
  0b01111111, // 8 -> усі
  0b01101111, // 9 -> a b c d f g
};

void setup() {
  for (uint8_t i = 0; i < 8; i++) pinMode(SEG_PIN[i], OUTPUT);
}

void showDigit(uint8_t d, bool dot) {
  uint8_t mask = DIGIT[d];
  if (dot) mask |= 0b10000000;              // засвітити крапку
  for (uint8_t i = 0; i < 8; i++)
    digitalWrite(SEG_PIN[i], (mask >> i) & 1);  // біт -> сегмент
}

void loop() {
  for (uint8_t d = 0; d < 10; d++) { showDigit(d, false); delay(700); }
}
