// ULN2003: клацаємо реле раз на секунду через канал 1.
// PA8 → IN1 (вивід 1 чипа). Реле: +5V → обмотка → OUT1 (вивід 16).
// COM (вивід 9) → +5V живлення реле — обов'язково, це вмикає гасильний діод.
// Ногу PA8 в CubeMX задано як GPIO_Output, push-pull, без підтяжки.
#define RELAY_PORT  GPIOA
#define RELAY_PIN   GPIO_PIN_8

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();                 // тут увімкнено такт порту й задано режим ноги

  while (1) {
    HAL_GPIO_WritePin(RELAY_PORT, RELAY_PIN, GPIO_PIN_SET);    // «1» на IN1 → OUT1 сідає на землю
    HAL_Delay(1000);
    HAL_GPIO_WritePin(RELAY_PORT, RELAY_PIN, GPIO_PIN_RESET);  // «0» → OUT1 відпускається
    HAL_Delay(1000);
  }
}
