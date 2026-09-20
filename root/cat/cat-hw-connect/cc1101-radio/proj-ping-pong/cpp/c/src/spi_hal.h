#ifndef SPI_HAL_H
#define SPI_HAL_H

#include <stdint.h>
#include <stdbool.h>

void spi_hal_init(void);
uint8_t spi_hal_transfer(uint8_t data);
void spi_hal_cs_low(void);
void spi_hal_cs_high(void);
bool spi_hal_is_miso_low(void);
bool spi_hal_get_gdo0(void); // Пін для перевірки статусу

#endif
