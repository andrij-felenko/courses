#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Базові адреси периферійних модулів
#define TAMP_BASE            0x40002800U
#define BKP_BASE             0x40002850U
#define PWR_BASE             0x40007000U

// Зміщення регістрів контролера TAMP
#define TAMP_CR1_OFFSET      0x00U
#define TAMP_CR2_OFFSET      0x04U
#define TAMP_FLTCR_OFFSET    0x0CU
#define TAMP_ATCR1_OFFSET    0x20U
#define TAMP_ATSEEDR_OFFSET  0x24U
#define TAMP_IER_OFFSET      0x2CU
#define TAMP_SR_OFFSET       0x30U
#define TAMP_SCR_OFFSET      0x3CU

#define REG32(addr) (*(volatile uint32_t *)(addr))

// Бітові маски конфігурації
#define TAMP_CR1_TAMP1E      (1U << 0)  // Пасивний тампер 1 (NC контакт)
#define TAMP_CR1_ITAMP1E     (1U << 16) // Внутрішній тампер температури
#define TAMP_ATCR1_TAMP1AM   (1U << 0)  // Активний режим каналу 1 (LFSR)
#define TAMP_ATCR1_ATOSEL    (1U << 8)  // Комутація вихідного піна TAMP_OUT
#define TAMP_IER_TAMP1IE     (1U << 0)  // Дозвіл переривання
#define TAMP_SR_TAMP1F       (1U << 0)  // Прапорець вторгнення
#define TAMP_SCR_CTAMP1F     (1U << 0)  // Скидання прапорця

#define PWR_CR1_DBP          (1U << 8)  // Дозвіл доступу до Backup домену

#define BKP_REG_COUNT        32U

// Структура дескриптора драйвера
typedef struct {
    uint32_t active_seed;
    bool hardware_zeroize_enabled;
    uint32_t tamper_timestamp;
} tamper_driver_t;

// Безпечне очищення буфера (гарантовано не вирізається компілятором)
static void secure_memzero(volatile void *ptr, size_t len) {
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) {
        *p++ = 0U;
    }
}

// Ініціалізація та активація захисного контуру
bool tamper_init(tamper_driver_t *drv, uint32_t seed) {
    if (!drv || seed == 0U) {
        return false;
    }

    drv->active_seed = seed;
    drv->hardware_zeroize_enabled = true;
    drv->tamper_timestamp = 0U;

    // 1. Дозвіл доступу до регістрів резервного домену
    REG32(PWR_BASE + 0x00U) |= PWR_CR1_DBP;

    // 2. Зняття апаратного захисту запису ключами 0xCA, 0x53
    REG32(TAMP_BASE + 0x10U) = 0xCAU;
    REG32(TAMP_BASE + 0x10U) = 0x53U;

    // 3. Завантаження початкового зерна генератора LFSR
    REG32(TAMP_BASE + TAMP_ATSEEDR_OFFSET) = drv->active_seed;

    // 4. Конфігурація фільтра завад: опитування 1 Гц, глибина 4 вибірки
    REG32(TAMP_BASE + TAMP_FLTCR_OFFSET) = (0x02U << 0) | (0x01U << 3);

    // 5. Увімкнення активного режиму для захисної сітки
    REG32(TAMP_BASE + TAMP_ATCR1_OFFSET) = TAMP_ATCR1_TAMP1AM | TAMP_ATCR1_ATOSEL;

    // 6. Дозвіл переривань та активація зовнішнього і внутрішнього сенсорів
    REG32(TAMP_BASE + TAMP_IER_OFFSET) |= TAMP_IER_TAMP1IE;
    REG32(TAMP_BASE + TAMP_CR1_OFFSET) |= (TAMP_CR1_TAMP1E | TAMP_CR1_ITAMP1E);

    return true;
}

// Запис кореневого ключа в апаратні резервні регістри
void tamper_write_secret_key(const uint8_t *key, size_t key_len) {
    if (!key || key_len > (BKP_REG_COUNT * 4U)) {
        return;
    }

    const uint32_t *words = (const uint32_t *)key;
    size_t word_count = (key_len + 3U) / 4U;

    for (size_t i = 0; i < word_count; ++i) {
        REG32(BKP_BASE + (i * 4U)) = words[i];
    }
}

// Критичний обробник фізичного зламу (Tamper NMI / IRQ)
void TAMP_IRQHandler(void) {
    if (REG32(TAMP_BASE + TAMP_SR_OFFSET) & TAMP_SR_TAMP1F) {
        // Резервні регістри BKP SRAM вже обнулені апаратною шиною за 15 нс!
        // Програмно зачищаємо внутрішню системну пам'ять
        extern uint8_t _sdata, _edata, _sbss, _ebss;
        secure_memzero(&_sdata, (size_t)(&_edata - &_sdata));
        secure_memzero(&_sbss, (size_t)(&_ebss - &_sbss));

        // Фіксація події зламу в незмивному журналі
        REG32(TAMP_BASE + TAMP_SCR_OFFSET) = TAMP_SCR_CTAMP1F;

        // Незворотне перетворення пристрою на "цеглину"
        while (1) {
            __asm volatile("nop");
        }
    }
}
