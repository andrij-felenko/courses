const uint8_t BUZ = 8;           // активний зумер висить прямо на виводі

void setup() {
  pinMode(BUZ, OUTPUT);
  digitalWrite(BUZ, LOW);        // на старті тиша
}

void loop() {
  digitalWrite(BUZ, HIGH);       // подали «плюс» → внутрішній генератор завив
  delay(120);
  digitalWrite(BUZ, LOW);        // зняли → замовк
  delay(3000);
}
