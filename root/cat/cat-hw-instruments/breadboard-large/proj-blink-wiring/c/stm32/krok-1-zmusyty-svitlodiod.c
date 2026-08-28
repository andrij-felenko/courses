// Ногу PB8 у CubeMX задано як GPIO_Output, push-pull, без підтяжки.
#define LED_PORT  GPIOB
#define LED_PIN   GPIO_PIN_8

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();               // тут увімкнено такт порту й ніжку оголошено виходом

  while (1) {
    HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_SET);    // тягне до живлення → LED світиться
    HAL_Delay(500);                                        // тримаємо так 500 мс
    HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_RESET);  // тягне до нуля → LED гасне
    HAL_Delay(500);                                        // тримаємо темряву 500 мс
  }
}
