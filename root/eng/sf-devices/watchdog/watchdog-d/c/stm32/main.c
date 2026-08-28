#include "stm32f4xx_hal.h"

IWDG_HandleTypeDef hiwdg;    // незалежний сторож від власного LSI-генератора

int main(void) {
  HAL_Init();
  SystemClock_Config();

  hiwdg.Instance       = IWDG;
  hiwdg.Init.Prescaler = IWDG_PRESCALER_128;  // LSI ≈ 32 кГц / 128 ≈ 250 тактів/с
  hiwdg.Init.Reload    = 1250;                // 1250 / 250 = 5 с таймауту
  HAL_IWDG_Init(&hiwdg);                      // Init одразу ЗАПУСКАЄ сторожа

  for (;;) {
    DoWork();                    // якщо завис ТУТ — до годівлі не дійде
    HAL_IWDG_Refresh(&hiwdg);    // дійшли здоровими → скидаємо лічильник
  }
}
