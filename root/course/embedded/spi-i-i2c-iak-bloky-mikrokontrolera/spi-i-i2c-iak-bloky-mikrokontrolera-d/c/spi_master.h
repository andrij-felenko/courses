#ifndef SPI_MASTER_H
#define SPI_MASTER_H

#include <stddef.h>
#include <stdint.h>

#include "mcu_regs.h"

typedef enum {
    SPI_MODE0 = 0,  /* CPOL=0 CPHA=0 — захоплення на першому (наростаючому) фронті */
    SPI_MODE1,      /* CPOL=0 CPHA=1 */
    SPI_MODE2,      /* CPOL=1 CPHA=0 */
    SPI_MODE3       /* CPOL=1 CPHA=1 — теж захоплення на наростаючому */
} spi_mode_t;

typedef enum {
    SPI_OK = 0,
    SPI_ERR_TIMEOUT,
    SPI_ERR_OVERRUN,
    SPI_ERR_MODE_FAULT,
    SPI_ERR_BUSY,
    SPI_ERR_ARG
} spi_status_t;

/* Бюджет опитування рахуємо в холостих ітераціях, а не в мікросекундах:
   на цьому рівні ще немає ані таймера, ані планувальника. */
#define SPI_POLL_BUDGET 100000U

/* br: 0..7 — дільник f_PCLK2 / 2^(br+1), тобто 0 -> /2, 3 -> /16, 7 -> /256 */
void spi1_master_init(spi_mode_t mode, uint8_t br);
void spi1_cs_select(void);
void spi1_cs_release(void);

spi_status_t spi_transfer_byte(spi_regs_t *spi, uint8_t tx, uint8_t *rx, uint32_t budget);
spi_status_t spi_transfer(spi_regs_t *spi, const uint8_t *tx, uint8_t *rx,
                          size_t len, uint32_t budget);
spi_status_t spi_wait_idle(spi_regs_t *spi, uint32_t budget);

/* Регламентні послідовності очищення аварійних прапорців (RM0090) */
void spi_clear_overrun(spi_regs_t *spi);
void spi_recover_mode_fault(spi_regs_t *spi);

#endif /* SPI_MASTER_H */
