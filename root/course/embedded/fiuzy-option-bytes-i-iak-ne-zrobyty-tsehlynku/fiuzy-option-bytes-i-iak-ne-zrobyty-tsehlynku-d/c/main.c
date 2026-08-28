#include <stdint.h>
#include <stdbool.h>

/* Базові адреси та зміщення регістрів Flash (на прикладі родини STM32G0/G4) */
#define FLASH_BASE_ADDR      0x40022000UL
#define FLASH_ACR            (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x00))
#define FLASH_KEYR           (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x08))
#define FLASH_OPTKEYR        (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x0C))
#define FLASH_SR             (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x10))
#define FLASH_CR             (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x14))
#define FLASH_OPTR           (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x20))

/* Бітові маски */
#define FLASH_SR_BSY         (1UL << 16)
#define FLASH_SR_PGSERR      (1UL << 7)
#define FLASH_SR_WRPERR      (1UL << 4)
#define FLASH_CR_LOCK        (1UL << 31)
#define FLASH_CR_OPTLOCK     (1UL << 30)
#define FLASH_CR_OPTSTRT     (1UL << 17)
#define FLASH_CR_OBL_LAUNCH  (1UL << 27)

/* Магічні ключі розблокування */
#define FLASH_KEY1           0x45670123UL
#define FLASH_KEY2           0xCDEF89ABUL
#define FLASH_OPTKEY1        0x08192A3BUL
#define FLASH_OPTKEY2        0x4C5D6E7FUL

#define TIMEOUT_CYCLES       1000000UL

typedef enum {
    OPT_SUCCESS = 0,
    OPT_ERR_BUSY_TIMEOUT,
    OPT_ERR_UNLOCK_FAILED,
    OPT_ERR_WRITE_FAILED,
    OPT_ERR_INVALID_VALUE
} OptionResult_t;

/* Очікування завершення операцій Flash */
static bool flash_wait_ready(void) {
    uint32_t timeout = TIMEOUT_CYCLES;
    while ((FLASH_SR & FLASH_SR_BSY) && --timeout) {
        __asm__ volatile("nop");
    }
    return (timeout > 0);
}

/* Безпечне оновлення RDP та BOR без ризику переходу в Level 2 */
OptionResult_t flash_set_rdp_level1_safe(void) {
    /* 1. Перевірка, що Flash вільна */
    if (!flash_wait_ready()) {
        return OPT_ERR_BUSY_TIMEOUT;
    }

    /* 2. Розблокування Flash Control Register */
    if (FLASH_CR & FLASH_CR_LOCK) {
        FLASH_KEYR = FLASH_KEY1;
        FLASH_KEYR = FLASH_KEY2;
        if (FLASH_CR & FLASH_CR_LOCK) {
            return OPT_ERR_UNLOCK_FAILED;
        }
    }

    /* 3. Розблокування Option Bytes Register */
    if (FLASH_CR & FLASH_CR_OPTLOCK) {
        FLASH_OPTKEYR = FLASH_OPTKEY1;
        FLASH_OPTKEYR = FLASH_OPTKEY2;
        if (FLASH_CR & FLASH_CR_OPTLOCK) {
            FLASH_CR |= FLASH_CR_LOCK;
            return OPT_ERR_UNLOCK_FAILED;
        }
    }

    /* 4. Очищення попередніх прапорців помилок у SR */
    FLASH_SR = FLASH_SR_PGSERR | FLASH_SR_WRPERR;

    /* 5. Читання поточного значення та модифікація */
    uint32_t optr = FLASH_OPTR;
    
    /* Сувора заборона випадкового запису 0xCC (Level 2) */
    uint8_t new_rdp = 0xBB; /* Встановлюємо безпечний Level 1 */
    optr &= ~0xFFUL;        /* Очищаємо біти RDP[7:0] */
    optr |= (uint32_t)new_rdp;

    /* Запис нового значення в тіньовий OPTR */
    FLASH_OPTR = optr;

    /* 6. Запуск фізичного програмування */
    FLASH_CR |= FLASH_CR_OPTSTRT;

    /* 7. Очікування запису */
    if (!flash_wait_ready()) {
        FLASH_CR |= (FLASH_CR_OPTLOCK | FLASH_CR_LOCK);
        return OPT_ERR_BUSY_TIMEOUT;
    }

    /* 8. Перевірка помилок */
    if (FLASH_SR & (FLASH_SR_PGSERR | FLASH_SR_WRPERR)) {
        FLASH_CR |= (FLASH_CR_OPTLOCK | FLASH_CR_LOCK);
        return OPT_ERR_WRITE_FAILED;
    }

    /* 9. Блокування регістрів назад */
    FLASH_CR |= (FLASH_CR_OPTLOCK | FLASH_CR_LOCK);

    /* 10. Перезавантаження Option Bytes (викликає системний ресет) */
    FLASH_CR |= FLASH_CR_OBL_LAUNCH;

    return OPT_SUCCESS;
}
