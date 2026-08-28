void setup() {
  // r, g, b — кожен 0..255
  rgbLedWrite(21, 0, 40, 0);   // тьмяно-зелений: «плата ожила»
}

void loop() {
  rgbLedWrite(21, 40, 0, 0);   // червоний
  delay(500);
  rgbLedWrite(21, 0, 0, 40);   // синій
  delay(500);
}
