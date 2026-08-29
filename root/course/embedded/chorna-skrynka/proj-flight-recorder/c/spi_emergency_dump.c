/* spi_emergency_dump.c — прямий побайтовий запис дампа в SPI-носій.
 * Викликається з обробника HardFault, тому не має права ні на що чекати
 * нескінченно: кожне очікування прапорця обмежене лічильником обертів. */
#include "spi_emergency_dump.h"
#include "flight_recorder_core.h"
#include "mcu_port.h"

/* Регістри SPI1 (розкладка ARM Cortex-M, STM32F4) */
#define SPI1_BASE_ADDR    0x40013000U
#define SPI_CR1_ADDR      (SPI1_BASE_ADDR + 0x00U)
#define SPI_CR2_ADDR      (SPI1_BASE_ADDR + 0x04U)
#define SPI_SR_ADDR       (SPI1_BASE_ADDR + 0x08U)
#define SPI_DR_ADDR       (SPI1_BASE_ADDR + 0x0CU)

#define SPI_CR1_SPE       (1U << 6)
#define SPI_CR2_RXDMAEN   (1U << 0)
#define SPI_CR2_TXDMAEN   (1U << 1)
#define SPI_CR2_ERRIE     (1U << 5)
#define SPI_CR2_RXNEIE    (1U << 6)
#define SPI_CR2_TXEIE     (1U << 7)

#define SPI_SR_RXNE       (1U << 0)
#define SPI_SR_TXE        (1U << 1)
#define SPI_SR_BSY        (1U << 7)

/* Chip Select на PA4: BSRR ставить біт у молодшій половині й скидає в старшій */
#define GPIOA_BSRR_ADDR   (0x40020000U + 0x18U)
#define CS_PIN            4U

/* Стеля очікування прапорця. На 84 МГц це десятки мілісекунд — більше, ніж
 * треба справному SPI, і менше, ніж вікно сторожового таймера. */
#define SPI_SPIN_LIMIT    200000U

/* Команди SPI FRAM (FM25V) і NOR Flash (W25Q, MX25) — набір спільний */
#define OPCODE_WREN       0x06U
#define OPCODE_WRITE      0x02U /* FRAM WRITE / Flash PAGE PROGRAM */
#define OPCODE_RDSR       0x05U
#define OPCODE_READ       0x03U
#define OPCODE_SECTOR_ERASE 0x20U

#define STATUS_WIP        (1U << 0) /* Flash: операція триває */
#define STATUS_WEL        (1U << 1) /* запис дозволено */

#define FLASH_PAGE_SIZE   256U
#define FLASH_SECTOR_SIZE 4096U

static void cs_low(void)  { mcu_reg_write(GPIOA_BSRR_ADDR, 1U << (CS_PIN + 16U)); }
static void cs_high(void) { mcu_reg_write(GPIOA_BSRR_ADDR, 1U << CS_PIN); }

/* Забрати шину в того, хто нею користувався до аварії: зняти запити DMA й
 * переривання (обслуговувати їх нікому), дочекатися кінця обміну, злити
 * недочитаний байт з приймача й переконатися, що блок увімкнений. */
static BlackBoxFlushStatus_t spi_takeover(void) {
    uint32_t cr2 = mcu_reg_read(SPI_CR2_ADDR);
    cr2 &= ~(SPI_CR2_TXDMAEN | SPI_CR2_RXDMAEN | SPI_CR2_TXEIE | SPI_CR2_RXNEIE | SPI_CR2_ERRIE);
    mcu_reg_write(SPI_CR2_ADDR, cr2);

    uint32_t spins = SPI_SPIN_LIMIT;
    while ((mcu_reg_read(SPI_SR_ADDR) & SPI_SR_BSY) != 0U) {
        if (--spins == 0U) {
            return BB_FLUSH_TIMEOUT;
        }
    }
    if ((mcu_reg_read(SPI_SR_ADDR) & SPI_SR_RXNE) != 0U) {
        (void)(*((volatile uint8_t*)SPI_DR_ADDR)); /* викинути чужий байт */
    }
    mcu_reg_write(SPI_CR1_ADDR, mcu_reg_read(SPI_CR1_ADDR) | SPI_CR1_SPE);
    cs_high();
    return BB_FLUSH_OK;
}

/* Повний дуплекс опитуванням: чекаємо TXE, кладемо байт у DR ВІСЬМИБІТНИМ
 * доступом (32-бітний запис зібрав би кадр із двох байтів), чекаємо RXNE,
 * забираємо відповідь. Без читання RXNE приймач переповниться на другій сотні. */
static BlackBoxFlushStatus_t spi_xfer(uint8_t out, uint8_t* in) {
    uint32_t spins = SPI_SPIN_LIMIT;
    while ((mcu_reg_read(SPI_SR_ADDR) & SPI_SR_TXE) == 0U) {
        if (--spins == 0U) {
            return BB_FLUSH_TIMEOUT;
        }
    }
    *((volatile uint8_t*)SPI_DR_ADDR) = out;

    spins = SPI_SPIN_LIMIT;
    while ((mcu_reg_read(SPI_SR_ADDR) & SPI_SR_RXNE) == 0U) {
        if (--spins == 0U) {
            return BB_FLUSH_TIMEOUT;
        }
    }
    uint8_t received = *((volatile uint8_t*)SPI_DR_ADDR);
    if (in != NULL) {
        *in = received;
    }
    return BB_FLUSH_OK;
}

static BlackBoxFlushStatus_t spi_send(uint8_t byte) {
    return spi_xfer(byte, NULL);
}

static BlackBoxFlushStatus_t read_status(uint8_t* status) {
    BlackBoxFlushStatus_t rc;
    cs_low();
    rc = spi_send(OPCODE_RDSR);
    if (rc == BB_FLUSH_OK) {
        rc = spi_xfer(0xFFU, status);
    }
    cs_high();
    return rc;
}

/* Дозвіл запису й перевірка, що мікросхема справді відповідає: якщо WEL не
 * піднявся, далі писати нема куди — краще повернути помилку, ніж мовчки
 * протактувати 4 кілобайти в порожнечу. */
static BlackBoxFlushStatus_t write_enable(void) {
    cs_low();
    BlackBoxFlushStatus_t rc = spi_send(OPCODE_WREN);
    cs_high();
    if (rc != BB_FLUSH_OK) {
        return rc;
    }

    uint8_t status = 0;
    rc = read_status(&status);
    if (rc != BB_FLUSH_OK) {
        return rc;
    }
    return ((status & STATUS_WEL) != 0U) ? BB_FLUSH_OK : BB_FLUSH_NO_DEVICE;
}

static BlackBoxFlushStatus_t wait_write_done(void) {
    uint32_t spins = SPI_SPIN_LIMIT;
    for (;;) {
        uint8_t status = 0;
        BlackBoxFlushStatus_t rc = read_status(&status);
        if (rc != BB_FLUSH_OK) {
            return rc;
        }
        if ((status & STATUS_WIP) == 0U) {
            return BB_FLUSH_OK;
        }
        if (--spins == 0U) {
            return BB_FLUSH_TIMEOUT;
        }
    }
}

static BlackBoxFlushStatus_t send_addr24(uint8_t opcode, uint32_t addr) {
    BlackBoxFlushStatus_t rc = spi_send(opcode);
    if (rc == BB_FLUSH_OK) { rc = spi_send((uint8_t)((addr >> 16) & 0xFFU)); }
    if (rc == BB_FLUSH_OK) { rc = spi_send((uint8_t)((addr >> 8) & 0xFFU)); }
    if (rc == BB_FLUSH_OK) { rc = spi_send((uint8_t)(addr & 0xFFU)); }
    return rc;
}

/* Перед будь-яким вивантаженням кадри мусять опинитися у фізичній SRAM:
 * на M7 вони інакше лишаються в кеші даних, і на носій піде застаріле. */
static const uint8_t* prepare_source(size_t* size) {
    const BlackBoxStorage_t* storage = blackbox_get_storage_ptr();
    *size = blackbox_get_storage_size();
    mcu_dcache_clean(storage, *size);
    return (const uint8_t*)storage;
}

BlackBoxFlushStatus_t spi_emergency_write(uint32_t dst_addr) {
    BlackBoxFlushStatus_t rc = spi_takeover();
    if (rc != BB_FLUSH_OK) {
        return rc;
    }

    size_t size = 0;
    const uint8_t* raw = prepare_source(&size);

    rc = write_enable();
    if (rc != BB_FLUSH_OK) {
        return rc;
    }

    cs_low();
    rc = send_addr24(OPCODE_WRITE, dst_addr);
    for (size_t i = 0; rc == BB_FLUSH_OK && i < size; ++i) {
        rc = spi_send(raw[i]);
    }
    cs_high();
    return rc;
}

BlackBoxFlushStatus_t spi_flash_erase_slot(uint32_t dst_addr) {
    BlackBoxFlushStatus_t rc = spi_takeover();
    if (rc != BB_FLUSH_OK) {
        return rc;
    }

    size_t size = blackbox_get_storage_size();
    uint32_t sector = dst_addr & ~(FLASH_SECTOR_SIZE - 1U);
    uint32_t last   = (dst_addr + (uint32_t)size - 1U) & ~(FLASH_SECTOR_SIZE - 1U);

    for (; sector <= last; sector += FLASH_SECTOR_SIZE) {
        rc = write_enable();
        if (rc != BB_FLUSH_OK) {
            return rc;
        }
        cs_low();
        rc = send_addr24(OPCODE_SECTOR_ERASE, sector);
        cs_high();
        if (rc != BB_FLUSH_OK) {
            return rc;
        }
        rc = wait_write_done(); /* стирання сектора — десятки мілісекунд */
        if (rc != BB_FLUSH_OK) {
            return rc;
        }
    }
    return BB_FLUSH_OK;
}

BlackBoxFlushStatus_t spi_emergency_write_flash(uint32_t dst_addr) {
    BlackBoxFlushStatus_t rc = spi_takeover();
    if (rc != BB_FLUSH_OK) {
        return rc;
    }

    size_t size = 0;
    const uint8_t* raw = prepare_source(&size);
    size_t written = 0;

    while (written < size) {
        /* Перша сторінка може починатися не з її межі — довжину ріжемо так,
         * щоб запис не перескочив через край сторінки й не загорнувся на її початок. */
        uint32_t page_addr   = dst_addr + (uint32_t)written;
        uint32_t page_offset = page_addr & (FLASH_PAGE_SIZE - 1U);
        size_t   chunk       = FLASH_PAGE_SIZE - page_offset;
        if (chunk > (size - written)) {
            chunk = size - written;
        }

        rc = write_enable();
        if (rc != BB_FLUSH_OK) {
            return rc;
        }

        cs_low();
        rc = send_addr24(OPCODE_WRITE, page_addr);
        for (size_t i = 0; rc == BB_FLUSH_OK && i < chunk; ++i) {
            rc = spi_send(raw[written + i]);
        }
        cs_high();
        if (rc != BB_FLUSH_OK) {
            return rc;
        }

        rc = wait_write_done();
        if (rc != BB_FLUSH_OK) {
            return rc;
        }
        written += chunk;
    }

    /* Швидка перевірка першого слова: у не стертий сектор NOR лише гасить біти,
     * тож замість дампа там була б суміш зі старим вмістом. */
    uint8_t probe[4] = {0, 0, 0, 0};
    cs_low();
    rc = send_addr24(OPCODE_READ, dst_addr);
    for (size_t i = 0; rc == BB_FLUSH_OK && i < sizeof(probe); ++i) {
        rc = spi_xfer(0xFFU, &probe[i]);
    }
    cs_high();
    if (rc != BB_FLUSH_OK) {
        return rc;
    }

    for (size_t i = 0; i < sizeof(probe); ++i) {
        if (probe[i] != raw[i]) {
            return BB_FLUSH_NOT_ERASED;
        }
    }
    return BB_FLUSH_OK;
}
