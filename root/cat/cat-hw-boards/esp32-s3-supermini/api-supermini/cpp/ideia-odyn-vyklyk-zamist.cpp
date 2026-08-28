#define RGB_PIN 48   // вбудований WS2812 на SuperMini

void setup() {
  neopixelWrite(RGB_PIN, 0, 0, 0);   // згасити на старті
}

void loop() {
  neopixelWrite(RGB_PIN, 30, 0, 0);  // червоний
  delay(400);
  neopixelWrite(RGB_PIN, 0, 30, 0);  // зелений
  delay(400);
  neopixelWrite(RGB_PIN, 0, 0, 30);  // синій
  delay(400);
}
