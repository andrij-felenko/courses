#define N_SLOTS  20
#define GUARD_US 800

/* На STM32 період міряє сам таймер: канал TIM2_CH1 у режимі input capture
   ловить фронт на PA0 і клацає CNT у CCR1 — без похибки входу в ISR. */
volatile uint32_t period   = 0;       // останній період між фронтами, мкс
volatile uint32_t lastEdge = 0;
volatile uint8_t  fresh    = 0;       // прапорець «є новий вимір»

void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim) {
  if (htim->Channel != HAL_TIM_ACTIVE_CHANNEL_1) return;
  uint32_t t  = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);
  uint32_t dt = t - lastEdge;         // проміжок від попереднього фронту
  if (dt >= GUARD_US) {               // мертвий час: відкидаємо дрижання
    period   = dt;                    // ← ось воно, T у мікросекундах
    lastEdge = t;
    fresh    = 1;
  }
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_TIM2_Init();                     // TIM2 з тактом 1 мкс, CH1 = input capture
  MX_USART2_UART_Init();
  HAL_TIM_IC_Start_IT(&htim2, TIM_CHANNEL_1);

  while (1) {
    if (!fresh) continue;
    __disable_irq();
    uint32_t T = period;              // знімок періоду, мкс
    fresh = 0;
    __enable_irq();

    // об/хв = 60 000 000 / (N · T);  60e6 бо T у мкс
    float rpm = 60000000.0f / (N_SLOTS * (float)T);
    char buf[48];
    int n = snprintf(buf, sizeof buf, "миттєво: %.0f об/хв\r\n", rpm);
    HAL_UART_Transmit(&huart2, (uint8_t *)buf, n, HAL_MAX_DELAY);
  }
}
