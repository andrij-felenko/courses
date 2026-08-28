// Низькобічний MOSFET-модуль на GPIO16, ШІМ 20 кГц, 8 біт
const int PIN_GATE = 16;
const int CH = 0, FREQ = 20000, RES = 8;   // 20 кГц — поза чутністю

void setup() {
  ledcSetup(CH, FREQ, RES);
  ledcAttachPin(PIN_GATE, CH);
  ledcWrite(CH, 0);                // старт із закритого ключа — навантаження вимкнено
}

void loop() {
  for (int d = 0; d <= 255; d++) { // плавний пуск: шпаруватість 0→100%
    ledcWrite(CH, d);
    delay(4);
  }
  delay(500);
}
