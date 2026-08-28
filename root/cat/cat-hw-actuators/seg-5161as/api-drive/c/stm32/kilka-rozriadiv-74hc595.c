#include "main.h"

// CubeMX: SPI1 у режимі Transmit Only Master, 8 біт, MSB First.
// MOSI → DS (пін 14), SCK → SHCP (пін 11). Засувку STCP ведемо самі.
extern SPI_HandleTypeDef hspi1;

#define LATCH_PORT  GPIOB
#define LATCH_PIN   GPIO_PIN_0    // STCP (RCLK) → пін 12 регістра

static void show_mask_595(uint8_t mask) {
  HAL_GPIO_WritePin(LATCH_PORT, LATCH_PIN, GPIO_PIN_RESET);  // засувка закрита
  HAL_SPI_Transmit(&hspi1, &mask, 1, HAL_MAX_DELAY);         // 8 бітів у регістр
  HAL_GPIO_WritePin(LATCH_PORT, LATCH_PIN, GPIO_PIN_SET);    // клац → на виходи
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_SPI1_Init();
  while (1) {
    show_mask_595(SA|SB|SC|SD|SG);            // «3»
    HAL_Delay(500);
  }
}
