#ifndef SPI_ASYNC_H
#define SPI_ASYNC_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "spi_master.h"

/* Викликається з контексту переривання, коли обмін завершено чи зірвано */
typedef void (*spi_done_cb_t)(spi_status_t status);

void spi1_async_init(void);

/* Обмін на перериваннях: по одному байту в польоті, CS тримає драйвер */
spi_status_t spi1_irq_start(const uint8_t *tx, uint8_t *rx, size_t len, spi_done_cb_t cb);

/* Обмін через DMA2: потік 3 канал 3 (TX), потік 2 канал 3 (RX) */
spi_status_t spi1_dma_start(const uint8_t *tx, uint8_t *rx, size_t len, spi_done_cb_t cb);

bool spi1_async_busy(void);

#endif /* SPI_ASYNC_H */
