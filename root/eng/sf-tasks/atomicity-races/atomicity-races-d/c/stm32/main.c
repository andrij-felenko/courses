volatile uint32_t pulses = 0;          // volatile — свіжість значення

void HAL_GPIO_EXTI_Callback(uint16_t pin) {   // обробник лише рахує
  if (pin == GPIO_PIN_0) pulses++;
}

void read_pulses(void) {
  __disable_irq();                     // ← критична секція: цілісно
  uint32_t n = pulses;                 //   «знімок» спільних даних
  pulses = 0;
  __enable_irq();                      // ← переривання знову ввімкнені
  // ... далі працюємо з локальним n, поза секцією ...
  printf("%lu\r\n", (unsigned long) n);  // повільний вивід — НЕ в секції
}
