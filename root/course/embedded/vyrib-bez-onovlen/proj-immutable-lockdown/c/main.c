#include <stdint.h>
#include <stdbool.h>

/* Регістри Flash-контролера мікроконтролера (типова архітектура ARM Cortex-M) */
#define FLASH_BASE_ADDR        0x40022000UL
#define FLASH_KEYR             (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x04))
#define FLASH_OPTKEYR          (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x08))
#define FLASH_SR               (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x0C))
#define FLASH_CR               (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x10))
#define FLASH_OPTR             (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x20))
#define FLASH_WRP1AR           (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x2C))

/* Ключі розблокування доступу до Option Bytes */
#define FLASH_KEY1             0x45670123UL
#define FLASH_KEY2             0xCDEF89ABUL
#define FLASH_OPTKEY1          0x08192A3BUL
#define FLASH_OPTKEY2          0x4C5D6E7FUL

/* Прапорці регістра статусу Flash */
#define FLASH_SR_BSY           (1UL << 16)
#define FLASH_SR_WRPERR        (1UL << 4)
#define FLASH_SR_PGAERR        (1UL << 5)

/* Керуючі біти */
#define FLASH_CR_LOCK          (1UL << 31)
#define FLASH_CR_OPTLOCK       (1UL << 30)
#define FLASH_CR_OPTSTRT       (1UL << 17)
#define FLASH_CR_OBL_LAUNCH    (1UL << 27)

/* Конфігурація RDP */
#define RDP_LEVEL_0_KEY        0xAAU
#define RDP_LEVEL_1_KEY        0xBBU
#define RDP_LEVEL_2_KEY        0xCCU   /* Незворотне апаратне замикання */

/* Адреси OTP-сектора для калібрування */
#define OTP_START_ADDR         0x1FFF7000UL
#define OTP_MAGIC_HEADER       0x5345414CUL /* ASCII "SEAL" */

typedef enum {
    LOCK_OK = 0,
    LOCK_ERR_OTP_INVALID,
    LOCK_ERR_FLASH_BUSY,
    LOCK_ERR_UNLOCK_FAIL,
    LOCK_ERR_WRITE_FAIL,
    LOCK_ERR_VERIFY_FAIL
} lock_status_t;

/* Перевірка наявності валідних заводських даних в OTP перед замиканням */
static bool verify_factory_otp_data(void) {
    const volatile uint32_t *otp = (const volatile uint32_t *)OTP_START_ADDR;
    if (otp[0] != OTP_MAGIC_HEADER) {
        return false; /* Калібрування ще не записано */
    }
    
    /* Контроль цілісності: обчислення бітової суми слів даних */
    uint32_t sum = 0;
    for (size_t i = 1; i < 8; ++i) {
        sum ^= otp[i];
    }
    return (sum != 0 && sum != 0xFFFFFFFFUL);
}

/* Очікування завершення внутрішніх операцій контролера Flash */
static lock_status_t flash_wait_ready(uint32_t timeout_loops) {
    while (FLASH_SR & FLASH_SR_BSY) {
        if (--timeout_loops == 0) {
            return LOCK_ERR_FLASH_BUSY;
        }
    }
    if (FLASH_SR & (FLASH_SR_WRPERR | FLASH_SR_PGAERR)) {
        FLASH_SR = FLASH_SR_WRPERR | FLASH_SR_PGAERR; /* Скидання помилок */
        return LOCK_ERR_WRITE_FAIL;
    }
    return LOCK_OK;
}

/* Розблокування Option Bytes контролера Flash */
static lock_status_t flash_unlock_options(void) {
    if (FLASH_CR & FLASH_CR_LOCK) {
        FLASH_KEYR = FLASH_KEY1;
        FLASH_KEYR = FLASH_KEY2;
    }
    if (FLASH_CR & FLASH_CR_LOCK) {
        return LOCK_ERR_UNLOCK_FAIL;
    }

    if (FLASH_CR & FLASH_CR_OPTLOCK) {
        FLASH_OPTKEYR = FLASH_OPTKEY1;
        FLASH_OPTKEYR = FLASH_OPTKEY2;
    }
    if (FLASH_CR & FLASH_CR_OPTLOCK) {
        return LOCK_ERR_UNLOCK_FAIL;
    }
    return LOCK_OK;
}

/* Повне блокування контролера Flash */
static void flash_lock_all(void) {
    FLASH_CR |= (FLASH_CR_OPTLOCK | FLASH_CR_LOCK);
}

/* Головна функція замикання виробу на заводському стенді */
lock_status_t factory_lockdown_device(void) {
    /* 1. Обов'язкова перевірка заводських констант */
    if (!verify_factory_otp_data()) {
        return LOCK_ERR_OTP_INVALID;
    }

    /* 2. Очікування готовності Flash */
    lock_status_t status = flash_wait_ready(500000);
    if (status != LOCK_OK) {
        return status;
    }

    /* 3. Розблокування Option Bytes */
    status = flash_unlock_options();
    if (status != LOCK_OK) {
        return status;
    }

    /* 4. Захист усіх секторів коду від запису (WRP від сторінки 0 до 127) */
    FLASH_WRP1AR = (127UL << 16) | (0UL);

    /* 5. Встановлення рівня захисту RDP Level 2 (0xCC) */
    uint32_t optr = FLASH_OPTR;
    optr &= ~0xFFUL;             /* Очищення поля RDP */
    optr |= RDP_LEVEL_2_KEY;     /* Встановлення 0xCC */
    FLASH_OPTR = optr;

    /* 6. Запуск фізичного програмування Option Bytes */
    FLASH_CR |= FLASH_CR_OPTSTRT;
    status = flash_wait_ready(500000);
    if (status != LOCK_OK) {
        flash_lock_all();
        return status;
    }

    /* 7. Замикаємо Flash перед застосуванням */
    flash_lock_all();

    /* 8. Апаратне перезавантаження Option Bytes (System Reset) */
    FLASH_CR |= FLASH_CR_OBL_LAUNCH;

    /* Код далі не виконується: OBL_LAUNCH викликає негайний холодний ребут кристала */
    while (1) {
        __asm__ volatile("nop");
    }
}
