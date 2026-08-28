/* nor_flash.h — Низькорівневий драйвер SPI NOR Flash мовою C */
#ifndef NOR_FLASH_H
#define NOR_FLASH_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define NOR_PAGE_SIZE       256U
#define NOR_SECTOR_SIZE     4096U
#define NOR_BLOCK_SIZE      65536U

#define CMD_READ_ID         0x9FU
#define CMD_WRITE_ENABLE    0x06U
#define CMD_WRITE_DISABLE   0x04U
#define CMD_READ_STATUS_1   0x05U
#define CMD_READ_DATA       0x03U
#define CMD_FAST_READ       0x0BU
#define CMD_PAGE_PROGRAM    0x02U
#define CMD_SECTOR_ERASE_4K 0x20U
#define CMD_BLOCK_ERASE_64K 0xD8U
#define CMD_CHIP_ERASE      0xC7U

#define STATUS_WIP_BIT      (1U << 0)  /* Write In Progress */
#define STATUS_WEL_BIT      (1U << 1)  /* Write Enable Latch */

typedef struct {
    void (*cs_assert)(void);
    void (*cs_deassert)(void);
    uint8_t (*spi_transfer_byte)(uint8_t byte);
    void (*spi_transmit)(const uint8_t *data, size_t len);
    void (*spi_receive)(uint8_t *data, size_t len);
    void (*delay_us)(uint32_t us);
} nor_spi_hal_t;

typedef struct {
    const nor_spi_hal_t *hal;
    uint8_t mfg_id;
    uint8_t memory_type;
    uint8_t capacity_id;
    uint32_t total_size_bytes;
} nor_flash_t;

typedef enum {
    NOR_OK = 0,
    NOR_ERR_TIMEOUT,
    NOR_ERR_INVALID_PARAM,
    NOR_ERR_ID_MISMATCH
} nor_status_t;

/* Публічний API драйвера */
nor_status_t nor_init(nor_flash_t *dev, const nor_spi_hal_t *hal);
nor_status_t nor_read(nor_flash_t *dev, uint32_t addr, uint8_t *buf, size_t len);
nor_status_t nor_erase_sector(nor_flash_t *dev, uint32_t sector_addr);
nor_status_t nor_erase_block(nor_flash_t *dev, uint32_t block_addr);
nor_status_t nor_write(nor_flash_t *dev, uint32_t addr, const uint8_t *data, size_t len);
nor_status_t nor_wait_busy(nor_flash_t *dev, uint32_t timeout_ms);

#endif /* NOR_FLASH_H */

/* nor_flash.c — Реалізація функцій драйвера NOR Flash */
#include "nor_flash.h"

static nor_status_t nor_write_enable(nor_flash_t *dev) {
    dev->hal->cs_assert();
    dev->hal->spi_transfer_byte(CMD_WRITE_ENABLE);
    dev->hal->cs_deassert();
    return NOR_OK;
}

nor_status_t nor_wait_busy(nor_flash_t *dev, uint32_t timeout_ms) {
    uint32_t elapsed_us = 0;
    const uint32_t timeout_us = timeout_ms * 1000U;

    while (elapsed_us <= timeout_us) {
        dev->hal->cs_assert();
        dev->hal->spi_transfer_byte(CMD_READ_STATUS_1);
        uint8_t status = dev->hal->spi_transfer_byte(0xFF);
        dev->hal->cs_deassert();

        if ((status & STATUS_WIP_BIT) == 0) {
            return NOR_OK; /* Чип завершив операцію */
        }

        dev->hal->delay_us(50);
        elapsed_us += 50;
    }
    return NOR_ERR_TIMEOUT;
}

nor_status_t nor_init(nor_flash_t *dev, const nor_spi_hal_t *hal) {
    if (!dev || !hal) return NOR_ERR_INVALID_PARAM;
    dev->hal = hal;

    dev->hal->cs_deassert();
    dev->hal->delay_us(1000); /* Стабілізація живлення після скидання */

    /* Читання ідентифікатора JEDEC ID */
    dev->hal->cs_assert();
    dev->hal->spi_transfer_byte(CMD_READ_ID);
    dev->mfg_id = dev->hal->spi_transfer_byte(0xFF);
    dev->memory_type = dev->hal->spi_transfer_byte(0xFF);
    dev->capacity_id = dev->hal->spi_transfer_byte(0xFF);
    dev->hal->cs_deassert();

    /* Якщо всі байти 0x00 або 0xFF — чип не відповідає на шині */
    if ((dev->mfg_id == 0x00 && dev->capacity_id == 0x00) ||
        (dev->mfg_id == 0xFF && dev->capacity_id == 0xFF)) {
        return NOR_ERR_ID_MISMATCH;
    }

    /* Розрахунок ємності: capacity_id = N відповідає 2^N байтів */
    if (dev->capacity_id >= 0x10 && dev->capacity_id <= 0x22) {
        dev->total_size_bytes = 1UL << dev->capacity_id;
    } else {
        dev->total_size_bytes = 0;
    }

    return nor_wait_busy(dev, 100);
}

nor_status_t nor_read(nor_flash_t *dev, uint32_t addr, uint8_t *buf, size_t len) {
    if (!dev || !buf || len == 0) return NOR_ERR_INVALID_PARAM;
    if (addr + len > dev->total_size_bytes) return NOR_ERR_INVALID_PARAM;

    nor_status_t st = nor_wait_busy(dev, 500);
    if (st != NOR_OK) return st;

    dev->hal->cs_assert();
    dev->hal->spi_transfer_byte(CMD_FAST_READ);
    dev->hal->spi_transfer_byte((uint8_t)(addr >> 16));
    dev->hal->spi_transfer_byte((uint8_t)(addr >> 8));
    dev->hal->spi_transfer_byte((uint8_t)(addr >> 0));
    dev->hal->spi_transfer_byte(0xFF); /* 1 Dummy-байт для Fast Read */

    dev->hal->spi_receive(buf, len);
    dev->hal->cs_deassert();

    return NOR_OK;
}

nor_status_t nor_erase_sector(nor_flash_t *dev, uint32_t sector_addr) {
    if (!dev) return NOR_ERR_INVALID_PARAM;
    sector_addr &= ~(NOR_SECTOR_SIZE - 1U); /* Вирівнювання на границю 4 КБ */

    nor_status_t st = nor_wait_busy(dev, 500);
    if (st != NOR_OK) return st;

    nor_write_enable(dev);

    dev->hal->cs_assert();
    dev->hal->spi_transfer_byte(CMD_SECTOR_ERASE_4K);
    dev->hal->spi_transfer_byte((uint8_t)(sector_addr >> 16));
    dev->hal->spi_transfer_byte((uint8_t)(sector_addr >> 8));
    dev->hal->spi_transfer_byte((uint8_t)(sector_addr >> 0));
    dev->hal->cs_deassert();

    return nor_wait_busy(dev, 500); /* Сектор стирається до 300–500 мс */
}

/* Внутрішній запис однієї сторінки (не більше 256 байтів у межах однієї сторінки) */
static nor_status_t nor_page_program(nor_flash_t *dev, uint32_t addr,
                                     const uint8_t *data, size_t len) {
    if (len > NOR_PAGE_SIZE) return NOR_ERR_INVALID_PARAM;

    nor_status_t st = nor_wait_busy(dev, 100);
    if (st != NOR_OK) return st;

    nor_write_enable(dev);

    dev->hal->cs_assert();
    dev->hal->spi_transfer_byte(CMD_PAGE_PROGRAM);
    dev->hal->spi_transfer_byte((uint8_t)(addr >> 16));
    dev->hal->spi_transfer_byte((uint8_t)(addr >> 8));
    dev->hal->spi_transfer_byte((uint8_t)(addr >> 0));
    dev->hal->spi_transmit(data, len);
    dev->hal->cs_deassert();

    return nor_wait_busy(dev, 50); /* Сторінка пишеться до 1–3 мс */
}

/* Безпечний запис масиву довільної довжини з розбиттям по межах сторінок 256 Б */
nor_status_t nor_write(nor_flash_t *dev, uint32_t addr, const uint8_t *data, size_t len) {
    if (!dev || !data || len == 0) return NOR_ERR_INVALID_PARAM;
    if (addr + len > dev->total_size_bytes) return NOR_ERR_INVALID_PARAM;

    while (len > 0) {
        /* Обчислення кількості байтів, що вміщуються до кінця поточної сторінки */
        uint32_t page_offset = addr % NOR_PAGE_SIZE;
        size_t chunk = NOR_PAGE_SIZE - page_offset;
        if (chunk > len) chunk = len;

        nor_status_t st = nor_page_program(dev, addr, data, chunk);
        if (st != NOR_OK) return st;

        addr += chunk;
        data += chunk;
        len  -= chunk;
    }
    return NOR_OK;
}
