void setup() {
  Serial.begin(115200);
  delay(300);
  if (psramFound())
    Serial.printf("PSRAM є: %u КБ усього, %u КБ вільно\n",
                  (unsigned)(ESP.getPsramSize()      / 1024),
                  (unsigned)(ESP.getFreePsram()      / 1024));
  else
    Serial.println("PSRAM не знайдено: увімкни її в Tools → PSRAM");
}
