#define N_SLOTS    20
#define GUARD_US   800
#define WINDOW_MS  1000               // вікно вимірювання, мс
#define BLOCKED    1                  // з калібрування

volatile uint32_t pulses   = 0;
volatile uint32_t lastEdge = 0;

void HAL_GPIO_EXTI_Callback(uint16_t pin) {
  if (pin != GPIO_PIN_0) return;
  uint32_t t = __HAL_TIM_GET_COUNTER(&htim2);   // TIM2 тактує 1 мкс
  if (t - lastEdge >= GUARD_US) { pulses++; lastEdge = t; }
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();                     // PA0 = EXTI0, фронт за BLOCKED
  MX_TIM2_Init();
  MX_USART2_UART_Init();
  HAL_TIM_Base_Start(&htim2);

  uint32_t tWin = HAL_GetTick(), pPrev = 0;
  while (1) {
    uint32_t now = HAL_GetTick();
    if (now - tWin < WINDOW_MS) continue;
    uint32_t dt = now - tWin;         // фактичний час вікна, мс (≈WINDOW_MS)
    tWin = now;

    __disable_irq();
    uint32_t p = pulses;
    __enable_irq();

    uint32_t dp = p - pPrev;          // приріст імпульсів за вікно
    pPrev = p;

    // об/хв = 60000 · dp / (N · dt);  60000 бо dt у мс
    float rpm = 60000.0f * dp / (N_SLOTS * (float)dt);
    char buf[48];                     // потрібна підтримка float у printf
    int n = snprintf(buf, sizeof buf, "швидкість: %.0f об/хв\r\n", rpm);
    HAL_UART_Transmit(&huart2, (uint8_t *)buf, n, HAL_MAX_DELAY);
  }
}
