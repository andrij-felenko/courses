/* spi_flash_driver.h — драйвер зовнішньої SPI-Flash, клієнт диспетчера живлення. */
#ifndef SPI_FLASH_DRIVER_H
#define SPI_FLASH_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define SPI_FLASH_PAGE_SIZE 256u

void     spi_flash_init(void);

/* Запис сторінки через DMA. Повертає false, якщо драйвер зайнятий або
 * запис вилазить за межу сторінки — мікросхема в такому разі загорне
 * адресу по колу й затре початок сторінки. */
bool     spi_flash_write_page_async(uint32_t address, const uint8_t *data, size_t len);

/* Викликати з головного циклу: знімає блокування, коли мікросхема
 * допекла сторінку. Поки не знято — глибокий сон заборонено. */
void     spi_flash_poll(void);

bool     spi_flash_busy(void);
uint32_t spi_flash_errors(void);

#endif /* SPI_FLASH_DRIVER_H */
