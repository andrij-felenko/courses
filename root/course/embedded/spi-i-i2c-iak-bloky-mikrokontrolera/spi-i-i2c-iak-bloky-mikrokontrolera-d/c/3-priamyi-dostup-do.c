#include <stdint.h>
#include <stdbool.h>

/* Базові адреси та структури регістрів SPI (аналог Cortex-M / STM32) */
typedef struct {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SR;
    volatile uint32_t DR;
    volatile uint32_t CRCPR;
    volatile uint32_t RXCRCR;
    volatile uint32_t TXCRCR;
    volatile uint32_t I2SCFGR;
} spi_registers_t;

#define SPI1_BASE        ((spi_registers_t *)0x40013000)

#define SPI_SR_RXNE      (1U << 0)
#define SPI_SR_TXE       (1U << 1)
#define SPI_SR_BSY       (1U << 7)
#define SPI_SR_OVR       (1U << 6)
#define SPI_SR_MODF      (1U << 5)

typedef enum {
    SPI_OK = 0,
    SPI_ERR_TIMEOUT,
    SPI_ERR_OVERRUN,
    SPI_ERR_MODE_FAULT
} spi_status_t;

/* Блокувальна синхронна передача/прийом байта (Full Duplex) з захистом за тайм-аутом */
spi_status_t spi_transfer_byte(spi_registers_t *spi, uint8_t tx_data, uint8_t *rx_data, uint32_t timeout_cycles) {
    uint32_t timeout = timeout_cycles;

    /* 1. Очікуємо звільнення буфера передачі */
    while (!(spi->SR & SPI_SR_TXE)) {
        if (--timeout == 0) return SPI_ERR_TIMEOUT;
    }

    /* 2. Записуємо байт для початку генерації такту SCK */
    spi->DR = tx_data;

    timeout = timeout_cycles;
    /* 3. Очікуємо надходження прийнятого байта в буфер прийому */
    while (!(spi->SR & SPI_SR_RXNE)) {
        if (spi->SR & SPI_SR_OVR) {
            /* Очищення OVR: читання DR, потім читання SR */
            (void)spi->DR;
            (void)spi->SR;
            return SPI_ERR_OVERRUN;
        }
        if (spi->SR & SPI_SR_MODF) {
            return SPI_ERR_MODE_FAULT;
        }
        if (--timeout == 0) return SPI_ERR_TIMEOUT;
    }

    /* 4. Забираємо прийнятий байт */
    if (rx_data) {
        *rx_data = (uint8_t)(spi->DR & 0xFF);
    } else {
        (void)spi->DR; /* Скидаємо прапорець RXNE читанням у пустоту */
    }

    return SPI_OK;
}
