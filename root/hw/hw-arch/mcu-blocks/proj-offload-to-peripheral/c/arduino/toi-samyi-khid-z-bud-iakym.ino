volatile bool tick = false;          // прапорець «настала мить» — ставить ISR

void IRAM_ATTR onTimer() {           // обробник: коротко, лише підняти прапорець
  tick = true;
}

void setup() {
  // таймер 0, дільник 80: лічильник цокає раз на мікросекунду (80 МГц / 80)
  hw_timer_t *t = timerBegin(0, 80, true);
  timerAttachInterrupt(t, &onTimer, true);
  timerAlarmWrite(t, 1000, true);    // спрацьовувати кожні 1000 мкс = 1 мс
  timerAlarmEnable(t);
}

void loop() {
  if (tick) {                        // ядро реагує, коли зручно, а відлік — залізний
    tick = false;
    // тут — робота строго раз на мілісекунду
  }
}
