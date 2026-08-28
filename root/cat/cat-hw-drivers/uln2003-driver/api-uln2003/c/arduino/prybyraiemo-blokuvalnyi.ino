unsigned long lastStepUs = 0;      // коли зробили попередній крок (мкс)
unsigned long stepIntervalUs = 2000;   // період між півкроками (2000 мкс = 2 мс)
int dir = +1;

void loop() {
  unsigned long now = micros();
  if (now - lastStepUs >= stepIntervalUs) {
    lastStepUs = now;
    if (dir > 0) idx = (idx + 1) % 8;
    else         idx = (idx + 7) % 8;
    applyStep(idx);
  }
  // ...тут програма вільна: читай кнопки, датчики, шли по UART...
}
