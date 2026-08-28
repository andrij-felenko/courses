// PB8 — GPIO_Output (LED); PB9 — GPIO_Input із Pull-up (кнопка на «−»).
#define LED_PORT  GPIOB
#define LED_PIN   GPIO_PIN_8
#define BTN_PORT  GPIOB
#define BTN_PIN   GPIO_PIN_9

#define DEBOUNCE_MS  30u              // поріг: скільки чекати, поки брязкіт уляжеться

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();                     // LED — вихід, кнопка — вхід із підтяжкою до «+»

  bool          led_on     = false;            // поточний стан світла (перемикач)
  GPIO_PinState btn_stable = GPIO_PIN_SET;     // усталений стан кнопки (відпущена = SET)
  GPIO_PinState btn_last   = GPIO_PIN_SET;     // що прочитали минулого разу
  uint32_t      last_edge  = 0;                // мить останнього дрижання на вході

  while (1) {
    GPIO_PinState reading = HAL_GPIO_ReadPin(BTN_PORT, BTN_PIN);

    // будь-яка зміна на вході — чи то натиск, чи то брязкіт — заводить годинник наново
    if (reading != btn_last) {
      last_edge = HAL_GetTick();
    }

    // вхід постояв незмінним досить довго — йому вже можна вірити
    if (HAL_GetTick() - last_edge > DEBOUNCE_MS) {
      if (reading != btn_stable) {
        btn_stable = reading;
        if (btn_stable == GPIO_PIN_RESET) {    // саме натиснули (active-low)
          led_on = !led_on;                    // перевертаємо світло
          HAL_GPIO_WritePin(LED_PORT, LED_PIN, led_on ? GPIO_PIN_SET : GPIO_PIN_RESET);
        }
      }
    }

    btn_last = reading;               // запам'ятали для наступного кола
  }
}
