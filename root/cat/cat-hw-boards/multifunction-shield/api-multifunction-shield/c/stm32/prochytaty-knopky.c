// STM32 HAL: кнопку опитує той самий тик таймера, у головний цикл іде вже подія
void shield_tick(void) {                       // 1 кГц
  static uint8_t stable, cnt;
  uint8_t now = (HAL_GPIO_ReadPin(BTN1_GPIO_Port, BTN1_Pin) == GPIO_PIN_RESET);
  if (now == stable) cnt = 0;                  // без змін — лічильник спокою обнуляється
  else if (++cnt >= 20) {                      // 20 однакових тиків = 20 мс без деренчання
    stable = now; cnt = 0;
    btn_push(now ? BTN_1_PRESSED : BTN_1_SHORT_RELEASE);
  }
}

uint8_t ev = btn_pop();                        // 0, якщо черга порожня — як getButton()
if (ev == BTN_1_SHORT_RELEASE) { /* ... робимо дію */ }
