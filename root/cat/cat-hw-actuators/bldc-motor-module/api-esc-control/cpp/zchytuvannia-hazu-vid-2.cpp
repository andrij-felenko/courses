void setup() {
  esc.attach(ESC_PIN, 1000, 2000);

  // Не рушати, поки оператор не поставить ручку в нуль.
  esc.writeMicroseconds(1000);
  while (map(analogRead(POT_PIN), 0, 1023, 1000, 2000) > 1050) {
    // тримаємо стоп і чекаємо, доки ручку скинуть донизу
    esc.writeMicroseconds(1000);
    delay(20);
  }
  delay(2000);   // тепер спокійно озброюємось на нулі
}
