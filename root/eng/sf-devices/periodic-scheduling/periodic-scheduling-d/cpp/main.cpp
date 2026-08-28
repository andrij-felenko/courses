struct Task {
  unsigned long period;   // як часто (мс)
  unsigned long last;     // коли востаннє
  void (*run)();          // що робити
};

Task tasks[] = {
  { 500,  0, toggleLed   },   // блимати
  { 100,  0, readSensor  },   // опитати давач
  { 1000, 0, updateLcd   },   // оновити екран
};

void loop() {
  unsigned long now = millis();
  for (Task &t : tasks)
    if (now - t.last >= t.period) {
      t.last += t.period;
      t.run();              // запускаємо дозрілу задачу
    }
}
