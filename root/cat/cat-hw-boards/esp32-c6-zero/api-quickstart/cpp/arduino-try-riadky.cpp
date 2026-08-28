#define POT_PIN  3     // IO3 — один із каналів ADC1

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);   // 0..4095 (це і є типове)
}

void loop() {
  int raw = analogRead(POT_PIN);          // 0..4095
  int mv  = analogReadMilliVolts(POT_PIN);  // одразу мілівольти, з калібруванням
  Serial.printf("raw=%d  U=%d мВ\n", raw, mv);
  delay(200);
}
