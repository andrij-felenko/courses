#include "main.h"                // BUZ_GPIO_Port / BUZ_Pin завів CubeMX

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();                // вивід зумера — GPIO_Output, push-pull
  HAL_GPIO_WritePin(BUZ_GPIO_Port, BUZ_Pin, GPIO_PIN_RESET);   // тиша

  while (1) {
    HAL_GPIO_WritePin(BUZ_GPIO_Port, BUZ_Pin, GPIO_PIN_SET);   // завив
    HAL_Delay(120);
    HAL_GPIO_WritePin(BUZ_GPIO_Port, BUZ_Pin, GPIO_PIN_RESET); // замовк
    HAL_Delay(3000);
  }
}
