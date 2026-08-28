uint32_t lastStepMs = 0;       // коли зробили попередній крок (мс)
uint32_t stepIntervalMs = 2;   // період між півкроками
int dir = +1;

while (1) {
  uint32_t now = HAL_GetTick();   // мс від старту, лічильник SysTick
  if (now - lastStepMs >= stepIntervalMs) {
    lastStepMs = now;
    if (dir > 0) idx = (idx + 1) % 8;
    else         idx = (idx + 7) % 8;
    apply_step(idx);
  }
  // ...тут програма вільна: читай кнопки, датчики, шли по UART...
}
