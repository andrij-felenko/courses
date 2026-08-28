int calMin = 1023;                   // почати з протилежних країв, щоб перше ж
int calMax = 0;                      // виміряне значення їх «стягнуло» до правди

// Викликати в циклі протягом кількох секунд, поки крутиш ручку від упору до упору.
void calibrateSweep() {
  int raw = analogRead(PIN_POT);
  if (raw < calMin) calMin = raw;
  if (raw > calMax) calMax = raw;
}

// Після калібрування: масштабувати від РЕАЛЬНИХ країв і затиснути в межі.
int potPercent() {
  int raw = analogRead(PIN_POT);
  int pct = map(raw, calMin, calMax, 0, 100);
  return constrain(pct, 0, 100);     // не вилазити за 0..100 через шум на краях
}
