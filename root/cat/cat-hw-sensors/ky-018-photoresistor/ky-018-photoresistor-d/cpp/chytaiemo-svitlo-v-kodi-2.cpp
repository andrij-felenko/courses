const uint8_t PIN_LDR = A0;
const uint8_t PIN_LED = 13;
const int     DARK    = 300;     // поріг: нижче — вважаємо «темно» (добери під себе!)

void setup() {
  pinMode(PIN_LED, OUTPUT);
}

void loop() {
  int light = analogRead(PIN_LDR);
  bool dark = (light < DARK);          // менше світла = менший відлік
  digitalWrite(PIN_LED, dark ? HIGH : LOW);
  delay(100);
}
