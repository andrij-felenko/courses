void setup() {
  Serial.begin(115200);
  // S3 піднімає USB-CDC не миттєво; коротко дочекаємось порту,
  // але не вічно — щоб плата працювала й без відкритого термінала.
  unsigned long t0 = millis();
  while (!Serial && millis() - t0 < 2000) { /* чекаємо до 2 с */ }

  Serial.println();
  Serial.println("ESP32-S3 SuperMini живий.");
  Serial.printf("Чип: %s, ревізія %d, ядер: %d\n",
                ESP.getChipModel(), ESP.getChipRevision(), ESP.getChipCores());
  Serial.printf("Вільна купа: %u байт\n", ESP.getFreeHeap());
}

void loop() {
  Serial.printf("аптайм: %lu мс\n", millis());
  delay(1000);
}
