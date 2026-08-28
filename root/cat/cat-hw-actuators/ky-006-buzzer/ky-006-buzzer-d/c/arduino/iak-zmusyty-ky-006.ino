const uint8_t PIN_BUZ = 8;

void setup() {
  pinMode(PIN_BUZ, OUTPUT);
}

void loop() {
  // один цикл меандру 1000 Гц: 500 мкс вгорі + 500 мкс унизу
  digitalWrite(PIN_BUZ, HIGH);
  delayMicroseconds(500);
  digitalWrite(PIN_BUZ, LOW);
  delayMicroseconds(500);
}
