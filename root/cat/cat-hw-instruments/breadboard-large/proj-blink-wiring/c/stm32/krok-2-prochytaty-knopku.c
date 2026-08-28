// PB8 у CubeMX — GPIO_Output; PB9 — GPIO_Input із Pull-up (внутрішня підтяжка до «+»).
#define LED_PORT  GPIOB
#define LED_PIN   GPIO_PIN_8
#define BTN_PORT  GPIOB
#define BTN_PIN   GPIO_PIN_9

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();               // тут задано напрямки ніжок і ввімкнено підтяжку на BTN_PIN

  while (1) {
    // active-low: натиснуто = RESET. Тож "світло є" ⇔ "на вході RESET".
    if (HAL_GPIO_ReadPin(BTN_PORT, BTN_PIN) == GPIO_PIN_RESET) {
      HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_SET);    // кнопку тримають → світимо
    } else {
      HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_RESET);  // відпущено → гасимо
    }
  }
}
