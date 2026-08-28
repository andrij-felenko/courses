/* spi_emergency_dump.c - Прямий автономний запис дампа у SPI FRAM / Flash (C) */
#include "flight_recorder_core.h"

/* Пряма адресація регістрів апаратного SPI1 (на прикладі ARM Cortex-M) */
#define SPI1_BASE_ADDR   0x40013000U
#define SPI_CR1_REG      (*((volatile uint32_t*)(SPI1_BASE_ADDR + 0x00U)))
#define SPI_SR_REG       (*((volatile uint32_t*)(SPI1_BASE_ADDR + 0x08U)))
#define SPI_DR_REG       (*((volatile uint32_t*)(SPI1_BASE_ADDR + 0x0CU)))
#define GPIOA_BSRR_REG   (*((volatile uint32_t*)(0x40020000U + 0x18U)))

#define SPI_SR_TXE_FLAG  (1U << 1)
#define SPI_SR_BSY_FLAG  (1U << 7)
#define FRAM_OPCODE_WREN 0x06U
#define FRAM_OPCODE_WRITE 0x02U

static void emergency_cs_low(void)  { GPIOA_BSRR_REG = (1U << (4 + 16)); } /* CS = Low  (PA4) */
static void emergency_cs_high(void) { GPIOA_BSRR_REG = (1U << 4); }        /* CS = High (PA4) */

static uint8_t emergency_spi_transfer_byte(uint8_t data) {
    while (!(SPI_SR_REG & SPI_SR_TXE_FLAG)) {
        /* Очікування звільнення буфера передавача без затримки RTOS */
    }
    SPI_DR_REG = data;
    while (SPI_SR_REG & SPI_SR_BSY_FLAG) {
        /* Очікування завершення тактування байта на лініях SCK/MOSI */
    }
    return (uint8_t)SPI_DR_REG;
}

void blackbox_spi_emergency_flush(uint32_t flash_dst_addr) {
    const BlackBoxStorage_t* storage = blackbox_get_storage_ptr();
    const uint8_t* raw_bytes = (const uint8_t*)storage;
    size_t total_size = sizeof(BlackBoxStorage_t);

    /* 1. Дозвіл запису (Write Enable Latch) */
    emergency_cs_low();
    emergency_spi_transfer_byte(FRAM_OPCODE_WREN);
    emergency_cs_high();

    /* 2. Передача команди запису та 24-бітної адреси сховища */
    emergency_cs_low();
    emergency_spi_transfer_byte(FRAM_OPCODE_WRITE);
    emergency_spi_transfer_byte((uint8_t)(flash_dst_addr >> 16));
    emergency_spi_transfer_byte((uint8_t)(flash_dst_addr >> 8));
    emergency_spi_transfer_byte((uint8_t)(flash_dst_addr & 0xFFU));

    /* 3. Потокова передача 4096 байтів дампа зі швидкістю тактування SPI */
    for (size_t i = 0; i < total_size; ++i) {
        emergency_spi_transfer_byte(raw_bytes[i]);
    }
    emergency_cs_high();
}
