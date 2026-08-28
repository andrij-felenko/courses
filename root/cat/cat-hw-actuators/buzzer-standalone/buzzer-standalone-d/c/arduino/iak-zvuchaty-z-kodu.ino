const uint8_t BUZ = 8;          // вивід, на якому висить активний зумер

void setup() {
  pinMode(BUZ, OUTPUT);
}

void beep(uint16_t ms) {         // короткий сигнал «сталася подія»
  digitalWrite(BUZ, HIGH);       // подали живлення — генератор усередині завив
  delay(ms);
  digitalWrite(BUZ, LOW);        // зняли — замовк
}

void loop() {
  beep(120);                     // піп
  delay(2000);
}
