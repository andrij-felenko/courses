int readAveraged(uint8_t samples = 8) {
  digitalWrite(PIN_POWER, HIGH);
  delay(10);                     // усталення — ОДИН раз на весь пакет вимірів
  long sum = 0;
  for (uint8_t i = 0; i < samples; i++) {
    sum += analogRead(PIN_SIGNAL);
    delay(2);                    // маленька пауза між вибірками
  }
  digitalWrite(PIN_POWER, LOW);  // знеструмили після всього пакета
  return (int)(sum / samples);
}
