#define N_SLOTS 20                // прорізів на диску

volatile uint32_t pulses = 0;     // лічильник; його чіпає ISR → volatile

/* PA0 налаштовано в CubeMX як GPIO_EXTI0, режим GPIO_MODE_IT_RISING,
   переривання EXTI0 увімкнено. HAL кличе цей колбек із обробника. */
void HAL_GPIO_EXTI_Callback(uint16_t pin) {
  if (pin == GPIO_PIN_0) pulses++;
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();                 // конфіг піна й EXTI від CubeMX
  MX_USART2_UART_Init();

  uint32_t tPrint = 0;
  while (1) {
    uint32_t now = HAL_GetTick(); // мілісекунди від старту
    if (now - tPrint >= 1000) {   // раз на секунду знімаємо зріз
      tPrint = now;

      __disable_irq();            // атомарно зчитуємо 32-бітне значення
      uint32_t p = pulses;
      __enable_irq();

      char buf[48];
      int n = snprintf(buf, sizeof buf, "обертів усього: %lu\r\n",
                       (unsigned long)(p / N_SLOTS));
      HAL_UART_Transmit(&huart2, (uint8_t *)buf, n, HAL_MAX_DELAY);
    }
  }
}
