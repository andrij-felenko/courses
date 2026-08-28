const uint8_t PIN_LDR = A0;      // S давача на аналоговому вході

void setup() {
  Serial.begin(9600);
}

void loop() {
  int light = analogRead(PIN_LDR);   // 0…1023 на 10-бітному АЦП Uno
  Serial.println(light);             // темно → мале число; світло → близько 1023
  delay(200);
}
