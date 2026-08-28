#include <stdint.h>
#include <stdbool.h>
#include "stm32h7xx.h"

/* Системні константи протоколу Flash W25Q128JV */
#define W25Q_CMD_READ_JEDEC_ID      0x9F
#define W25Q_CMD_WRITE_ENABLE       0x06
#define W25Q_CMD_READ_STATUS_REG1   0x05
#define W25Q_CMD_READ_STATUS_REG2   0x35
#define W25Q_CMD_WRITE_STATUS_REG2  0x31
#define W25Q_CMD_FAST_READ_QUAD_IO  0xEB

#define W25Q_STATUS1_BUSY_MASK      0x01
#define W25Q_STATUS2_QE_MASK        0x02
#define W25Q_MODE_CONTINUOUS_READ   0xA5

/* Очікування завершення транзакції за прапорцем TCF */
static inline void qspi_wait_transfer_complete(void) {
    while (!(QUADSPI->SR & QUADSPI_SR_TCF)) {
        /* Очікування апаратного прапорця Transfer Complete */
    }
    QUADSPI->FCR = QUADSPI_FCR_CTCF;
}

/* Очікування переходу кінцевого автомата QSPI у стан спокою */
static inline void qspi_wait_idle(void) {
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {
        /* Очікування скидання біта зайнятості BUSY */
    }
}

/* Апаратне автоопитування статусу готовності Flash (скидання біта BUSY) */
static bool qspi_auto_poll_busy(uint32_t timeout_cycles) {
    QUADSPI->PSMKR = W25Q_STATUS1_BUSY_MASK;
    QUADSPI->PSMAR = 0x00; /* Очікуємо BUSY == 0 */
    QUADSPI->PIR   = 0x10; /* Період опитування: 16 тактів */
    
    /* Конфігурація автоопитування: команда 0x05, 1 лінія, FMODE = 10b */
    QUADSPI->CR |= (QUADSPI_CR_APMS | QUADSPI_CR_PMM); // Зупинка автомата при збігу
    QUADSPI->CCR = (2U << QUADSPI_CCR_FMODE_Pos) |     // Automatic Status-Polling
                   (1U << QUADSPI_CCR_DMODE_Pos) |     // 1 лінія даних
                   (1U << QUADSPI_CCR_IMODE_Pos) |     // 1 лінія інструкції
                   W25Q_CMD_READ_STATUS_REG1;

    while (!(QUADSPI->SR & QUADSPI_SR_SMF)) {
        if (--timeout_cycles == 0) {
            QUADSPI->CR |= QUADSPI_CR_ABORT;
            qspi_wait_idle();
            return false;
        }
    }
    QUADSPI->FCR = QUADSPI_FCR_CSMF;
    qspi_wait_idle();
    return true;
}

/* Повна ініціалізація та переведення QSPI Flash у режим XIP */
bool qspi_init_xip(void) {
    /* 1. Активація тактування QSPI та необхідних портів GPIO */
    RCC->AHB3ENR |= RCC_AHB3ENR_QSPIEN;
    RCC->AHB4ENR |= RCC_AHB4ENR_GPIOBEN | RCC_AHB4ENR_GPIOEEN;

    /* 2. Конфігурація виводів: PB2 (CLK), PB6 (CS), PE7..PE10 (IO0..IO3) */
    GPIOB->OSPEEDR |= (3U << (2 * 2)) | (3U << (6 * 2));
    GPIOE->OSPEEDR |= (3U << (7 * 2)) | (3U << (8 * 2)) | (3U << (9 * 2)) | (3U << (10 * 2));

    GPIOB->PUPDR |= (1U << (6 * 2)); /* Підтяжка CS# до VDD */
    GPIOE->PUPDR |= (1U << (7 * 2)) | (1U << (8 * 2)) | (1U << (9 * 2)) | (1U << (10 * 2));

    GPIOB->AFR[0] |= (9U << (2 * 4)) | (10U << (6 * 4)); /* PB2->AF9, PB6->AF10 */
    GPIOE->AFR[0] |= (10U << (7 * 4));                   /* PE7->AF10 */
    GPIOE->AFR[1] |= (10U << ((8 - 8) * 4)) | (10U << ((9 - 8) * 4)) | (10U << ((10 - 8) * 4));

    GPIOB->MODER &= ~((3U << (2 * 2)) | (3U << (6 * 2)));
    GPIOB->MODER |=  ((2U << (2 * 2)) | (2U << (6 * 2))); /* Alternate Function */
    GPIOE->MODER &= ~((3U << (7 * 2)) | (3U << (8 * 2)) | (3U << (9 * 2)) | (3U << (10 * 2)));
    GPIOE->MODER |=  ((2U << (7 * 2)) | (2U << (8 * 2)) | (2U << (9 * 2)) | (2U << (10 * 2)));

    /* 3. Базове налаштування QSPI: дільник = 1 (100 МГц @ 200 МГц AHB), FSIZE = 23 (16 МБ) */
    QUADSPI->CR = (1U << QUADSPI_CR_PRESCALER_Pos) | QUADSPI_CR_SSHIFT | QUADSPI_CR_EN;
    QUADSPI->DCR = (23U << QUADSPI_DCR_FSIZE_Pos) | (4U << QUADSPI_DCR_CSHT_Pos);

    /* 4. Зчитування JEDEC ID для перевірки наявності та типу чипа */
    uint8_t jedec[3] = {0};
    QUADSPI->DLR = 3 - 1; /* 3 байти */
    QUADSPI->CCR = (1U << QUADSPI_CCR_FMODE_Pos) | /* Indirect Read */
                   (1U << QUADSPI_CCR_DMODE_Pos) | /* 1 лінія даних */
                   (1U << QUADSPI_CCR_IMODE_Pos) | /* 1 лінія команди */
                   W25Q_CMD_READ_JEDEC_ID;

    for (int i = 0; i < 3; i++) {
        while (!(QUADSPI->SR & (QUADSPI_SR_FTF | QUADSPI_SR_TCF))) {}
        jedec[i] = *(volatile uint8_t *)&QUADSPI->DR;
    }
    qspi_wait_transfer_complete();
    qspi_wait_idle();

    if (jedec[0] != 0xEF) { /* 0xEF = Winbond Vendor ID */
        return false;
    }

    /* 5. Дозвіл запису (Write Enable) */
    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_IMODE_Pos) | W25Q_CMD_WRITE_ENABLE;
    qspi_wait_transfer_complete();
    qspi_wait_idle();

    /* 6. Встановлення біта Quad Enable (QE) у Status Register-2 */
    QUADSPI->DLR = 1 - 1;
    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | /* Indirect Write */
                   (1U << QUADSPI_CCR_DMODE_Pos) | 
                   (1U << QUADSPI_CCR_IMODE_Pos) | 
                   W25Q_CMD_WRITE_STATUS_REG2;
    *(volatile uint8_t *)&QUADSPI->DR = W25Q_STATUS2_QE_MASK;
    qspi_wait_transfer_complete();
    qspi_wait_idle();

    /* Очікування завершення внутрішнього програмування комірок Flash */
    if (!qspi_auto_poll_busy(1000000)) {
        return false;
    }

    /* 7. Переведення контролера в режим Memory-Mapped (0-4-4 Continuous Read) */
    QUADSPI->ABR = W25Q_MODE_CONTINUOUS_READ;
    QUADSPI->CCR = (3U << QUADSPI_CCR_FMODE_Pos) |  // Memory-Mapped Mode (11b)
                   QUADSPI_CCR_SIOO |               // Send Instruction Only Once (0-4-4)
                   (4U << QUADSPI_CCR_DCYC_Pos) |   // 4 Dummy такти
                   (1U << QUADSPI_CCR_ABSIZE_Pos)|  // 8-бітне поле Mode Bits
                   (3U << QUADSPI_CCR_ABMODE_Pos)|  // Mode Bits по 4 лініях
                   (2U << QUADSPI_CCR_ADSIZE_Pos)|  // 24-бітна адреса
                   (3U << QUADSPI_CCR_ADMODE_Pos)|  // Адреса по 4 лініях
                   (3U << QUADSPI_CCR_DMODE_Pos) |  // Дані по 4 лініях
                   (1U << QUADSPI_CCR_IMODE_Pos) |  // Команда по 1 лінії (для 1-го разу)
                   W25Q_CMD_FAST_READ_QUAD_IO;

    return true;
}

/* Налаштування MPU та увімкнення апаратного L1-кешу Cortex-M7 */
void qspi_enable_cache(void) {
    ARM_MPU_Disable();

    /* Область 0: 16 МБайт QSPI Flash за адресою 0x90000000 */
    ARM_MPU_SetRegion(
        ARM_MPU_RBAR(0, 0x90000000U),
        ARM_MPU_RASR(
            0,                          /* Дозвіл виконання коду (XN = 0) */
            ARM_MPU_AP_RO,              /* Права: Read-Only */
            ARM_MPU_ACCESS_NORMAL(
                ARM_MPU_CACHEP_WB_WRA,  /* Write-Back, Write-Allocate */
                ARM_MPU_CACHEP_WB_WRA
            ),
            0x00,                       /* Усі підрегіони дозволені */
            ARM_MPU_REGION_SIZE_16MB    /* Розмір регіону 16 МБ */
        )
    );

    ARM_MPU_Enable(MPU_CTRL_PRIVDEFENA_Msk);

    /* Активація L1 кешу інструкцій та даних */
    SCB_InvalidateICache();
    SCB_EnableICache();
    
    SCB_InvalidateDCache();
    SCB_EnableDCache();
}
