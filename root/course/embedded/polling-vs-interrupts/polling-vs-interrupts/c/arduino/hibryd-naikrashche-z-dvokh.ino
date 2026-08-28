int prev = LOW;
volatile unsigned long turns = 0;

void loop() {
  int now = digitalRead(SENSOR_PIN);   // питаємо ніжку самі
  if (prev == LOW && now == HIGH)      // зловили висхідний фронт?
    turns++;
  prev = now;
  // ... решта роботи циклу: екран, мережа, обрахунки ...
}
