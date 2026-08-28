void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000) { }   // трохи чекаємо, поки хост відкриє порт
  Serial.println("привіт із рідного USB");
}

void loop() {
  Serial.printf("uptime: %lu c\n", millis() / 1000);
  delay(1000);
}
