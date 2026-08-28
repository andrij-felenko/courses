#include "stm32f4xx_hal.h"

extern SPI_HandleTypeDef hspi1;   // частоту (дільник) і режим задано в MX_SPI1_Init();
                                  // SCK/MISO/MOSI прибиті до блоку SPI1 — вибору ніг нема
#define CS_PORT GPIOA
#define CS_PIN  GPIO_PIN_4        // CS — звичайний GPIO, смикаємо руками

// один обмін байтом з веденим пристроєм
uint8_t spi_exchange(uint8_t out) {
  uint8_t in = 0;
  HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_RESET);   // вибрали пристрій
  HAL_SPI_TransmitReceive(&hspi1, &out, &in, 1, 100);   // шлемо out і читаємо in
  HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);     // відпустили
  return in;
}
