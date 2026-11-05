#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define QSPI_CMD_READ_STATUS        0x05U
#define QSPI_CMD_WRITE_ENABLE       0x06U
#define QSPI_CMD_PAGE_PROGRAM_QUAD  0x32U
#define QSPI_CMD_SECTOR_ERASE_4K    0x20U

#define QSPI_STATUS_WIP_BIT         (1U << 0)
#define FLASH_PAGE_SIZE             256U
#define FLASH_SECTOR_SIZE           4096U
#define CACHE_LINE_SIZE             32U

/* Статуси виконання низькорівневих апаратних операцій */
typedef enum {
    HW_FLASH_IDLE = 0,
    HW_FLASH_BUSY,
    HW_FLASH_SUCCESS,
    HW_FLASH_ERR_TIMEOUT,
    HW_FLASH_ERR_ALIGNMENT,
    HW_FLASH_ERR_DMA
} hw_flash_status_t;

/* Апаратні регістри периферійного контролера QSPI */
typedef struct {
    volatile uint32_t CR;
    volatile uint32_t DCR;
    volatile uint32_t SR;
    volatile uint32_t FCR;
    volatile uint32_t DLR;
    volatile uint32_t CCR;
    volatile uint32_t AR;
    volatile uint32_t ABR;
    volatile uint32_t DR;
    volatile uint32_t PSMKR;
    volatile uint32_t PSMAR;
    volatile uint32_t PIR;
    volatile uint32_t LPTR;
} qspi_hw_regs_t;

/* Апаратні регістри каналу контролера DMA */
typedef struct {
    volatile uint32_t CCR;
    volatile uint32_t CNDTR;
    volatile uint32_t CPAR;
    volatile uint32_t CMAR;
} dma_channel_hw_regs_t;

/* Апаратні регістри прискорювача CRC */
typedef struct {
    volatile uint32_t DR;
    volatile uint32_t IDR;
    volatile uint32_t CR;
    volatile uint32_t INIT;
    volatile uint32_t POL;
} crc_hw_regs_t;

/* Контекст апаратного драйвера спалах-пам'яті */
typedef struct {
    qspi_hw_regs_t        *qspi;
    dma_channel_hw_regs_t *dma;
    crc_hw_regs_t         *crc;
    volatile bool          dma_transfer_done;
    uint32_t               base_address;
} qspi_driver_t;

/* Апаратний бар'єр синхронізації даних */
static inline void hw_barrier_dsb(void) {
    __asm__ volatile("dsb 0xF" ::: "memory");
}

/* Апаратний бар'єр синхронізації інструкцій */
static inline void hw_barrier_isb(void) {
    __asm__ volatile("isb 0xF" ::: "memory");
}

/* Очищення брудних ліній кеша даних за адресою через регістри ядра Cortex-M7 SCB */
static void hw_dcache_clean_range(const void *addr, uint32_t size) {
    volatile uint32_t *dccmvac = (volatile uint32_t *)0xE000EF68U;
    uintptr_t start = (uintptr_t)addr & ~(uintptr_t)(CACHE_LINE_SIZE - 1U);
    uintptr_t end = (uintptr_t)addr + size;

    while (start < end) {
        *dccmvac = (uint32_t)start;
        start += CACHE_LINE_SIZE;
    }
    hw_barrier_dsb();
}

/* Ініціалізація драйвера периферії */
void qspi_driver_init(qspi_driver_t *drv,
                      qspi_hw_regs_t *qspi_base,
                      dma_channel_hw_regs_t *dma_channel,
                      crc_hw_regs_t *crc_base,
                      uint32_t base_addr) {
    drv->qspi = qspi_base;
    drv->dma = dma_channel;
    drv->crc = crc_base;
    drv->dma_transfer_done = false;
    drv->base_address = base_addr;

    /* Скидання прапорців та увімкнення QSPI контролера */
    drv->qspi->FCR = 0x1FU;
    drv->qspi->CR |= (1U << 0); /* EN bit */

    /* Ініціалізація апаратного блоку CRC поліномом Ethernet/ZIP */
    if (drv->crc) {
        drv->crc->POL = 0x04C11DB7U;
        drv->crc->INIT = 0xFFFFFFFFU;
        drv->crc->CR = 1U; /* Скидання розрахунку */
    }
}

/* Передача команди дозволу запису WREN */
static void qspi_send_write_enable(qspi_driver_t *drv) {
    drv->qspi->FCR = 0x1FU;
    /* Конфігурація CCR: 1 провід інструкції, без адреси, без даних, команда 0x06 */
    drv->qspi->CCR = (1U << 8) | QSPI_CMD_WRITE_ENABLE;
    while ((drv->qspi->SR & (1U << 1)) == 0) {
        /* Очікування завершення передачі команди (TCF прапорець) */
    }
    drv->qspi->FCR = (1U << 1);
}

/* Неблокуюча перевірка статусу зайнятості мікросхеми Flash */
hw_flash_status_t qspi_poll_status(qspi_driver_t *drv) {
    drv->qspi->FCR = 0x1FU;
    drv->qspi->DLR = 0; /* Очікуємо 1 байт */
    /* CCR: 1 лінія команди, 1 лінія даних, команда Read Status 0x05 */
    drv->qspi->CCR = (1U << 24) | (1U << 8) | QSPI_CMD_READ_STATUS;

    while ((drv->qspi->SR & (1U << 2)) == 0) {
        /* Очікування байта у вхідному FIFO (FTF прапорець) */
    }

    uint8_t status_reg = (uint8_t)(drv->qspi->DR);
    drv->qspi->FCR = 0x1FU;

    if (status_reg & QSPI_STATUS_WIP_BIT) {
        return HW_FLASH_BUSY;
    }
    return HW_FLASH_IDLE;
}

/* Асинхронний запуск програмування 256-байтної сторінки через DMA */
hw_flash_status_t qspi_program_page_async(qspi_driver_t *drv,
                                          uint32_t flash_offset,
                                          const uint8_t *data_page) {
    if (((uintptr_t)data_page & (CACHE_LINE_SIZE - 1U)) != 0) {
        return HW_FLASH_ERR_ALIGNMENT;
    }

    if (qspi_poll_status(drv) == HW_FLASH_BUSY) {
        return HW_FLASH_BUSY;
    }

    /* Очищення брудних ліній D-Cache для гарантії узгодженості пам'яті з DMA */
    hw_dcache_clean_range(data_page, FLASH_PAGE_SIZE);

    /* Активація режиму запису мікросхеми Flash */
    qspi_send_write_enable(drv);

    drv->dma_transfer_done = false;

    /* Налаштування DMA каналу: напрямок пам'ять -> периферія, розмір 8 біт */
    drv->dma->CCR &= ~1U; /* Вимкнення для налаштування */
    drv->dma->CPAR = (uint32_t)&(drv->qspi->DR);
    drv->dma->CMAR = (uint32_t)data_page;
    drv->dma->CNDTR = FLASH_PAGE_SIZE;
    drv->dma->CCR = (1U << 4) | (1U << 7) | (1U << 1); /* DIR=пам'ять->периферія, MINC=1, TCIE=1 */

    /* Налаштування регістрів QSPI для Quad Page Program */
    drv->qspi->DLR = FLASH_PAGE_SIZE - 1U;
    drv->qspi->AR = drv->base_address + flash_offset;
    /* 1 лінія команди, 1 лінія адреси 24 біт, 4 лінії даних Quad, DMA увімкнено */
    drv->qspi->CR |= (1U << 2); /* DMAEN */
    drv->qspi->CCR = (3U << 24) | (2U << 12) | (1U << 8) | QSPI_CMD_PAGE_PROGRAM_QUAD;

    /* Запуск передачі даних контролером DMA */
    drv->dma->CCR |= 1U;
    hw_barrier_dsb();

    return HW_FLASH_BUSY;
}

/* Апаратне стирання сектора 4 КБ */
hw_flash_status_t qspi_erase_sector_4k(qspi_driver_t *drv, uint32_t sector_offset) {
    if (qspi_poll_status(drv) == HW_FLASH_BUSY) {
        return HW_FLASH_BUSY;
    }

    qspi_send_write_enable(drv);

    drv->qspi->FCR = 0x1FU;
    drv->qspi->AR = drv->base_address + sector_offset;
    /* Команда стирання: 1 лінія інструкції, 1 лінія адреси 24 біт, без даних */
    drv->qspi->CCR = (2U << 12) | (1U << 8) | QSPI_CMD_SECTOR_ERASE_4K;

    while ((drv->qspi->SR & (1U << 1)) == 0) {
        /* Очікування завершення видачі команди на шину */
    }
    drv->qspi->FCR = (1U << 1);

    return HW_FLASH_BUSY;
}

/* Обробник переривання завершення транзакції DMA каналу */
void qspi_dma_isr_handler(qspi_driver_t *drv) {
    drv->dma->CCR &= ~1U;
    drv->qspi->CR &= ~(1U << 2); /* Вимикаємо DMAEN */
    drv->dma_transfer_done = true;
    hw_barrier_isb();
}

/* Апаратне обчислення CRC32 чергового блоку дельти */
uint32_t qspi_hw_crc32_feed(qspi_driver_t *drv, const uint8_t *data, uint32_t len) {
    if (!drv->crc) {
        return 0;
    }
    const uint32_t *words = (const uint32_t *)data;
    uint32_t word_count = len / 4U;

    for (uint32_t i = 0; i < word_count; ++i) {
        drv->crc->DR = words[i];
    }
    return drv->crc->DR;
}
