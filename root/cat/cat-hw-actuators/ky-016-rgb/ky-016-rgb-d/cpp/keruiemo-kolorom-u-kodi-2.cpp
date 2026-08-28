const uint8_t PIN_R = 9, PIN_G = 10, PIN_B = 11;

void setColor(uint8_t r, uint8_t g, uint8_t b) {
  analogWrite(PIN_R, r);
  analogWrite(PIN_G, g);
  analogWrite(PIN_B, b);
}

// позиція 0..255 по «колесу»: перетікання Ч→З→С→Ч
void wheel(uint8_t pos) {
  if (pos < 85)        setColor(255 - pos * 3, pos * 3, 0);          // червоний → зелений
  else if (pos < 170) { pos -= 85; setColor(0, 255 - pos * 3, pos * 3); } // зелений → синій
  else                { pos -= 170; setColor(pos * 3, 0, 255 - pos * 3); } // синій → червоний
}

void setup() {}

void loop() {
  for (int p = 0; p < 256; p++) {   // повний оберт колеса
    wheel(p);
    delay(15);                      // швидкість перетікання
  }
}
