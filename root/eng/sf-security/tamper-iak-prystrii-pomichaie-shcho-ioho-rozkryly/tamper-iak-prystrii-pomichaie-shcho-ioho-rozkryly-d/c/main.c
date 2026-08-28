#include <stdint.h>
#include <stdbool.h>

// Базові адреси периферійного блоку TAMP
#define TAMP_BASE_ADDR        0x40002800U
#define BKP_BASE_ADDR         0x40002850U
#define TAMP_CR1              (*(volatile uint32_t *)(TAMP_BASE_ADDR + 0x00U))
#define TAMP_ATCR1            (*(volatile uint32_t *)(TAMP_BASE_ADDR + 0x20U))
#define TAMP_ATSEEDR          (*(volatile uint32_t *)(TAMP_BASE_ADDR + 0x24U))
#define TAMP_IER              (*(volatile uint32_t *)(TAMP_BASE_ADDR + 0x2CU))
#define TAMP_SR               (*(volatile uint32_t *)(TAMP_BASE_ADDR + 0x30U))
#define TAMP_SCR              (*(volatile uint32_t *)(TAMP_BASE_ADDR + 0x3CU))

#define TAMP_CR1_TAMP1E       (1U << 0)   // Дозвіл каналу 1 (активна сітка)
#define TAMP_CR1_ITAMP1E      (1U << 16)  // Дозвіл монітора температури
#define TAMP_ATCR1_TAMP1AM    (1U << 0)   // Активний режим генерації LFSR
#define TAMP_IER_TAMP1IE      (1U << 0)   // Дозвіл переривання
#define TAMP_SR_TAMP1F        (1U << 0)   // Прапорець тривоги
#define TAMP_SCR_CTAMP1F      (1U << 0)   // Очищення тривоги

// Захищене від оптимізації компілятора занулення пам'яті
static void zeroize_buffer(volatile uint8_t *buf, uint32_t len) {
    while (len--) {
        *buf++ = 0x00U;
    }
}

// Ініціалізація захисного контуру
void security_tamper_setup(uint32_t dynamic_seed) {
    // 1. Запис динамічного зерна для псевдовипадкового генератора LFSR
    TAMP_ATSEEDR = dynamic_seed;

    // 2. Увімкнення активного режиму для захисної сітки (Mesh Shield)
    TAMP_ATCR1 |= TAMP_ATCR1_TAMP1AM;

    // 3. Дозвіл переривання та активація моніторингу сітки й температури
    TAMP_IER |= TAMP_IER_TAMP1IE;
    TAMP_CR1 |= (TAMP_CR1_TAMP1E | TAMP_CR1_ITAMP1E);
}

// Критичний обробник фізичного зламу (Tamper NMI / IRQ)
void Security_Tamper_IRQHandler(void) {
    if (TAMP_SR & TAMP_SR_TAMP1F) {
        // Резервні ключі в BKP SRAM вже знищені апаратно!
        // Програмно зачищаємо внутрішню системну пам'ять
        extern uint8_t _sdata, _edata, _sbss, _ebss;
        zeroize_buffer(&_sdata, (uint32_t)(&_edata - &_sdata));
        zeroize_buffer(&_sbss, (uint32_t)(&_ebss - &_sbss));

        // Фіксація факту розкриття в незмивному регістрі статусу
        TAMP_SCR = TAMP_SCR_CTAMP1F;

        // Вхід у вічний безвихідний стан (перетворення на "цеглину")
        while (1) {
            __asm volatile("nop");
        }
    }
}
