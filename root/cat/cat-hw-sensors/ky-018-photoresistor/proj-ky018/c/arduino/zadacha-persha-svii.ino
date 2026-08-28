const uint8_t PIN_LDR = A0;

int rawMin = 1023;   // почнемо з «перевернутих» меж, щоб перший же відлік їх стягнув
int rawMax = 0;

void calibrate(uint16_t seconds) {
  uint32_t until = millis() + (uint32_t)seconds * 1000;
  while (millis() < until) {
    int v = analogRead(PIN_LDR);
    if (v < rawMin) rawMin = v;    // побачили темніше — опустили дно
    if (v > rawMax) rawMax = v;    // побачили світліше — підняли стелю
    delay(5);
  }
}
