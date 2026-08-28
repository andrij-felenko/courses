#include "main.h"                   // BUZ_GPIO_Port / BUZ_Pin — з генератора CubeMX

static void beep(uint16_t ms) {      // короткий сигнал «сталася подія»
  // генератор усередині завив
  HAL_GPIO_WritePin(BUZ_GPIO_Port, BUZ_Pin, GPIO_PIN_SET);
  HAL_Delay(ms);
  // зняли — замовк
  HAL_GPIO_WritePin(BUZ_GPIO_Port, BUZ_Pin, GPIO_PIN_RESET);
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();                    // тут вивід стає виходом push-pull
  while (1) {
    beep(120);                       // піп
    HAL_Delay(2000);
  }
}
