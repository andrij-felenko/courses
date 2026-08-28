const uint8_t PIN_POT = A0;      // повзунок потенціометра

void setup() {
  Serial.begin(9600);
  // аналоговий вхід не треба конфігурувати pinMode — analogRead налаштує сам
}

void loop() {
  int raw = analogRead(PIN_POT);           // 0..1023: сира частка ходу
  int pct = map(raw, 0, 1023, 0, 100);     // те саме у відсотках 0..100
  Serial.print(raw);
  Serial.print("  ->  ");
  Serial.print(pct);
  Serial.println(" %");
  delay(100);
}
