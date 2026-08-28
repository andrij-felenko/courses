#include <stdint.h>
#include <stdbool.h>

/* Регістри підсистеми тактування RCC (Reset and Clock Control) для STM32 */
#define RCC_BASE            0x40023800U
#define RCC_CR              (*(volatile uint32_t *)(RCC_BASE + 0x00U))
#define RCC_CFGR            (*(volatile uint32_t *)(RCC_BASE + 0x08U))
#define RCC_CSR             (*(volatile uint32_t *)(RCC_BASE + 0x74U))

/* Бітові маски керування тактуванням */
#define RCC_CR_HSION        (1U << 0)
#define RCC_CR_HSIRDY       (1U << 1)
#define RCC_CR_HSEON        (1U << 16)
#define RCC_CR_HSERDY       (1U << 17)
#define RCC_CR_CSSON        (1U << 19)

#define RCC_CFGR_SW_HSI     (0x00U << 0)
#define RCC_CFGR_SW_HSE     (0x01U << 0)
#define RCC_CFGR_SWS_MASK   (0x03U << 2)
#define RCC_CFGR_SWS_HSE    (0x01U << 2)

#define RCC_CSR_RMVF        (1U << 24)
#define RCC_CSR_PORRSTF     (1U << 27)
#define RCC_CSR_PINRSTF     (1U << 26)

#define HSE_STARTUP_TIMEOUT 0x5000U

typedef enum {
    RESET_CAUSE_COLD_POWER_ON,
    RESET_CAUSE_EXTERNAL_PIN,
    RESET_CAUSE_OTHER
} reset_cause_t;

/* Діагностика причини скидання за апаратними прапорцями RCC_CSR */
reset_cause_t hardware_diagnose_reset_cause(void) {
    reset_cause_t cause = RESET_CAUSE_OTHER;
    uint32_t csr = RCC_CSR;

    if (csr & RCC_CSR_PORRSTF) {
        cause = RESET_CAUSE_COLD_POWER_ON;
    } else if (csr & RCC_CSR_PINRSTF) {
        cause = RESET_CAUSE_EXTERNAL_PIN;
    }

    /* Очищення прапорців скидання */
    RCC_CSR |= RCC_CSR_RMVF;
    return cause;
}

/* Безпечний запуск зовнішнього кварцового генератора HSE з fallback на HSI */
bool hardware_clock_init_hse(void) {
    uint32_t timeout = HSE_STARTUP_TIMEOUT;

    /* 1. Переконуємося, що внутрішній HSI активний */
    RCC_CR |= RCC_CR_HSION;
    while (!(RCC_CR & RCC_CR_HSIRDY)) {}

    /* 2. Подаємо сигнал запуску на генератор HSE */
    RCC_CR |= RCC_CR_HSEON;

    /* 3. Очікуємо стабілізації амплітуди коливань резонатора */
    while (!(RCC_CR & RCC_CR_HSERDY) && (--timeout > 0)) {}

    if (timeout == 0) {
        /* Апаратний збій кварцу: вимикаємо HSE і лишаємося на HSI */
        RCC_CR &= ~RCC_CR_HSEON;
        return false;
    }

    /* 4. Перемикаємо системну шину SYSCLK на джерело HSE */
    RCC_CFGR = (RCC_CFGR & ~0x03U) | RCC_CFGR_SW_HSE;

    /* 5. Очікуємо підтвердження апаратного перемикання комутатора */
    while ((RCC_CFGR & RCC_CFGR_SWS_MASK) != RCC_CFGR_SWS_HSE) {}

    /* 6. Активуємо Clock Security System (CSS) для апаратного контролю */
    RCC_CR |= RCC_CR_CSSON;

    return true;
}
