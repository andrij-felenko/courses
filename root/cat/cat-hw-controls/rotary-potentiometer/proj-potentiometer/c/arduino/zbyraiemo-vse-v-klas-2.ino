const uint8_t PIN_POT = A0;
const uint8_t PIN_LED = 9;           // ШІМ-вихід під світлодіод

Potentiometer pot(PIN_POT, 4, 4);    // пін A0, SHIFT=4 (α≈0.06), мертва зона 4

void setup() {
  Serial.begin(9600);
  pinMode(PIN_LED, OUTPUT);
  pot.begin();

  // 3-секундне калібрування: крути ручку від упору до упору.
  Serial.println("Калібрування: крути ручку від краю до краю...");
  uint32_t t0 = millis();
  while (millis() - t0 < 3000) { pot.calibrate(); delay(5); }
  Serial.println("Готово.");
}

void loop() {
  int bright;
  // яскравість 0..255; подія лише коли ручку реально крутнули
  if (pot.changed(&bright, 0, 255)) {
    analogWrite(PIN_LED, bright);
    Serial.print("яскравість = ");
    Serial.println(bright);
  }
  delay(10);
}
