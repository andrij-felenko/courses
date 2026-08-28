#include <stdint.h>
#include <stdbool.h>

// Симуляція регістрів RCC для демонстрації
typedef struct {
    volatile uint32_t APB1RSTR; // Регістр скидання периферії APB1
    volatile uint32_t APB1ENR;  // Регістр тактування периферії APB1
} simulated_rcc_t;

static simulated_rcc_t g_rcc = { 0, 0 };

#define SIM_RCC_APB1RSTR_I2C1RST  (1U << 21)
#define SIM_RCC_APB1ENR_I2C1EN    (1U << 21)

// Безпечне скидання та реініціалізація модуля I2C1
void i2c1_hardware_reset_c(void) {
    // 1. Переконатися, що тактування шини активне
    g_rcc.APB1ENR |= SIM_RCC_APB1ENR_I2C1EN;
    (void)g_rcc.APB1ENR; // Бар'єр затримки

    // 2. Встановити апаратне скидання модуля
    g_rcc.APB1RSTR |= SIM_RCC_APB1RSTR_I2C1RST;
    (void)g_rcc.APB1RSTR; // Фіксація запису на шині

    // 3. Затримка для гарантованого скидання внутрішніх автоматів
    for (volatile int i = 0; i < 10; ++i) {
        __asm volatile("nop");
    }

    // 4. Зняти апаратне скидання
    g_rcc.APB1RSTR &= ~SIM_RCC_APB1RSTR_I2C1RST;
    (void)g_rcc.APB1RSTR; // Фіксація зняття скидання
}
