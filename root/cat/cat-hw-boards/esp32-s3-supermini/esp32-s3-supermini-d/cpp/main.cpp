#define RGB_PIN 48   // вбудований WS2812 на SuperMini

void setup() {
  // зелений на повну; аргументи — GPIO, R, G, B (0..255)
  neopixelWrite(RGB_PIN, 0, 40, 0);   // не 255 — діод яскравий, 40 досить
}

void loop() {
  neopixelWrite(RGB_PIN, 40, 0, 0);   // червоний
  delay(500);
  neopixelWrite(RGB_PIN, 0, 0, 40);   // синій
  delay(500);
}
