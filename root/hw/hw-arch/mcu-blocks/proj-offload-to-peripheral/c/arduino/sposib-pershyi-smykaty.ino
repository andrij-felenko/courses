const int PIN = 18;

void setup() {
  pinMode(PIN, OUTPUT);
}

void loop() {
  // ШІМ ~1 кГц, шпаруватість 50 %: 500 мкс «1», 500 мкс «0»
  digitalWrite(PIN, HIGH);
  delayMicroseconds(500);
  digitalWrite(PIN, LOW);
  delayMicroseconds(500);
}
