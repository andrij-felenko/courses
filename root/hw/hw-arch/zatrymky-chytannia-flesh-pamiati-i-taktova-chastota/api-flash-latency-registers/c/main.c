#include <stdint.h>
#include <stdbool.h>

#define FLASH_BASE_ADDR      0x40023C00U
#define FLASH_ACR_REG        (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x00U))

#define FLASH_ACR_LATENCY_MASK  (0x0FU)
#define FLASH_ACR_PRFTEN_BIT    (1U << 8)
#define FLASH_ACR_ICEN_BIT      (1U << 9)
#define FLASH_ACR_DCEN_BIT      (1U << 10)
#define FLASH_ACR_ICRST_BIT     (1U << 11)
#define FLASH_ACR_DCRST_BIT     (1U << 12)

typedef enum {
    FLASH_LATENCY_0WS = 0,
    FLASH_LATENCY_1WS = 1,
    FLASH_LATENCY_2WS = 2,
    FLASH_LATENCY_3WS = 3,
    FLASH_LATENCY_4WS = 4,
    FLASH_LATENCY_5WS = 5,
    FLASH_LATENCY_6WS = 6,
    FLASH_LATENCY_7WS = 7
} flash_latency_t;

/* Встановлення затримки з обов'язковим опитуванням бітів підтвердження */
bool flash_set_latency(flash_latency_t latency) {
    uint32_t acr = FLASH_ACR_REG;
    acr &= ~FLASH_ACR_LATENCY_MASK;
    acr |= ((uint32_t)latency & FLASH_ACR_LATENCY_MASK);
    FLASH_ACR_REG = acr;

    /* Цикл підтвердження запису: очікуємо, поки логіка Flash зафіксує затримку */
    uint32_t timeout = 1000U;
    while ((FLASH_ACR_REG & FLASH_ACR_LATENCY_MASK) != (uint32_t)latency) {
        if (--timeout == 0U) {
            return false; /* Апаратна помилка або збій шини */
        }
    }
    return true;
}

/* Увімкнення черги випереджального читання та кешів ART */
void flash_enable_accelerators(bool prefetch, bool icache, bool dcache) {
    uint32_t acr = FLASH_ACR_REG;
    if (prefetch) acr |= FLASH_ACR_PRFTEN_BIT; else acr &= ~FLASH_ACR_PRFTEN_BIT;
    if (icache)   acr |= FLASH_ACR_ICEN_BIT;   else acr &= ~FLASH_ACR_ICEN_BIT;
    if (dcache)   acr |= FLASH_ACR_DCEN_BIT;   else acr &= ~FLASH_ACR_DCEN_BIT;
    FLASH_ACR_REG = acr;
}

/* Примусова інвалідація кешів після оновлення Flash (IAP / Flash write) */
void flash_invalidate_caches(void) {
    /* Скидання кешів дозволено лише при вимкнених бітах ICEN / DCEN */
    FLASH_ACR_REG &= ~(FLASH_ACR_ICEN_BIT | FLASH_ACR_DCEN_BIT);
    
    /* Запис 1 в біти скидання */
    FLASH_ACR_REG |= (FLASH_ACR_ICRST_BIT | FLASH_ACR_DCRST_BIT);
    
    /* Біти скидання автоматично очищаються апаратурою; вмикаємо кеші назад */
    FLASH_ACR_REG &= ~(FLASH_ACR_ICRST_BIT | FLASH_ACR_DCRST_BIT);
    FLASH_ACR_REG |= (FLASH_ACR_ICEN_BIT | FLASH_ACR_DCEN_BIT);
}
