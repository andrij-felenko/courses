const uint8_t PIN_POWER  = 7;    // цифрова ніжка живить «+» HW-038
const uint8_t PIN_SIGNAL = A0;   // аналоговий вхід ← S (OUT) давача

void setup() {
  pinMode(PIN_POWER, OUTPUT);
  digitalWrite(PIN_POWER, LOW);  // за замовчуванням гребінка знеструмлена
}

int readRaw() {
  digitalWrite(PIN_POWER, HIGH); // подали живлення на гребінку
  delay(10);                     // ~10 мс, щоб сигнал усталився
  int v = analogRead(PIN_SIGNAL);
  digitalWrite(PIN_POWER, LOW);  // ОДРАЗУ зняли — гребінка під струмом лише ці 10 мс
  return v;
}
