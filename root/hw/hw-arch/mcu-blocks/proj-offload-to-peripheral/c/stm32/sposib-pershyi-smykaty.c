// ніжку вже налаштовано як вихід (CubeMX: PA5, Output Push Pull)
static void delay_us(uint32_t us) {          // HAL уміє лише HAL_Delay() у мілісекундах —
  uint32_t t0 = DWT->CYCCNT;                 // мікросекунди доводиться крутити самим
  uint32_t n  = us * (SystemCoreClock / 1000000U);
  while (DWT->CYCCNT - t0 < n) { }
}

while (1) {
  // ШІМ ~1 кГц, шпаруватість 50 %: 500 мкс «1», 500 мкс «0»
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
  delay_us(500);
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);
  delay_us(500);
}
