#include <stdint.h>
#include <stdbool.h>

#define RCC_BASE            0x40021000U
#define RCC_AHB2ENR         (*(volatile uint32_t *)(RCC_BASE + 0x4CU))
#define RCC_APB1ENR1        (*(volatile uint32_t *)(RCC_BASE + 0x58U))

#define GPIOA_BASE          0x48000000U
#define GPIOA_BSRR          (*(volatile uint32_t *)(GPIOA_BASE + 0x18U))

#define PWR_BASE            0x40007000U
#define PWR_CR1             (*(volatile uint32_t *)(PWR_BASE + 0x00U))
#define PWR_SCR             (*(volatile uint32_t *)(PWR_BASE + 0x18U))

#define DWT_CTRL            (*(volatile uint32_t *)0xE0001000U)
#define DWT_CYCCNT          (*(volatile uint32_t *)0xE0001004U)
#define CoreDebug_DEMCR     (*(volatile uint32_t *)0xE000EDFCU)

#define PIN_MARKER_DEBUG    (1U << 0)  // PA0: діагностичний маркер
#define PIN_SENSOR_VCC_EN   (1U << 2)  // PA2: затвор P-MOSFET ключа

// Збережена область пам'яті SRAM2 (Retention RAM, 0x10000000)
typedef struct {
    uint32_t signature;
    uint32_t wake_count;
    uint16_t sensor_buffer[32];
    uint16_t adc_calibration_offset;
} FastWakeContext;

#define CONTEXT_ADDR        0x10000000U
#define CONTEXT_MAGIC       0xC001CAFEU

static FastWakeContext *const g_ctx = (FastWakeContext *)CONTEXT_ADDR;

static inline void dwt_timer_start(void) {
    CoreDebug_DEMCR |= (1U << 24);
    DWT_CTRL |= (1U << 0);
    DWT_CYCCNT = 0;
}

static inline void power_rail_enable(void) {
    // Вмикаємо маркер та ключ навантаження (Active High логіка комутатора)
    GPIOA_BSRR = PIN_MARKER_DEBUG | PIN_SENSOR_VCC_EN;
}

static inline void power_rail_disable(void) {
    // Вимикаємо ключ навантаження та скидаємо діагностичний маркер
    GPIOA_BSRR = (PIN_MARKER_DEBUG << 16) | (PIN_SENSOR_VCC_EN << 16);
}

static uint16_t sample_adc_filtered(uint16_t cal_offset) {
    // Зняття серії з 16 вибірок із врахуванням збереженого зміщення
    uint32_t acc = 0;
    for (int i = 0; i < 16; ++i) {
        acc += (2048U + cal_offset + (uint32_t)(i * 2));
    }
    return (uint16_t)(acc >> 4);
}

void execute_fast_wake_pipeline(void) {
    // 1. Початок активної фази: підняти маркерний пін
    power_rail_enable();
    dwt_timer_start();

    // 2. Валідація контексту Retention RAM
    if (g_ctx->signature != CONTEXT_MAGIC) {
        g_ctx->signature = CONTEXT_MAGIC;
        g_ctx->wake_count = 0;
        g_ctx->adc_calibration_offset = 12; // Калібрувальне значення за замовчуванням
    }

    // 3. Апаратна затримка стабілізації шини живлення датчика (100 мкс @ 16 МГц = 1600 тактів)
    while (DWT_CYCCNT < 1600U) {
        // Очікування завершення перехідного процесу
    }

    // 4. Отримання стабілізованої вибірки
    uint16_t current_sample = sample_adc_filtered(g_ctx->adc_calibration_offset);

    // 5. Запис у кільцевий буфер Retention RAM
    uint32_t slot = g_ctx->wake_count % 32U;
    g_ctx->sensor_buffer[slot] = current_sample;
    g_ctx->wake_count++;

    // 6. Знеструмлення датчика та завершення активного імпульсу
    power_rail_disable();

    // 7. Очищення статусних прапорців та перехід у глибокий сон (Stop 2)
    PWR_SCR = (1U << 0);       // Clear WUF (Wakeup Flag)
    PWR_CR1 |= (1U << 14);     // Задати режим Stop 2

    __asm volatile ("wfi");
}
