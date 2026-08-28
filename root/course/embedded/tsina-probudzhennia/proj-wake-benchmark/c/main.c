#include <stdint.h>
#include <stdbool.h>

// Адреси регістрів периферії (приклад STM32L4 Cortex-M4)
#define RCC_BASE        0x40021000U
#define RCC_AHB2ENR     (*(volatile uint32_t *)(RCC_BASE + 0x4CU))
#define RCC_APB1ENR1    (*(volatile uint32_t *)(RCC_BASE + 0x58U))

#define GPIOA_BASE      0x48000000U
#define GPIOA_MODER     (*(volatile uint32_t *)(GPIOA_BASE + 0x00U))
#define GPIOA_BSRR      (*(volatile uint32_t *)(GPIOA_BASE + 0x18U))

#define PWR_BASE        0x40007000U
#define PWR_CR1         (*(volatile uint32_t *)(PWR_BASE + 0x00U))
#define PWR_SCR         (*(volatile uint32_t *)(PWR_BASE + 0x18U))

#define DWT_CTRL        (*(volatile uint32_t *)0xE0001000U)
#define DWT_CYCCNT      (*(volatile uint32_t *)0xE0001004U)
#define CoreDebug_DEMCR (*(volatile uint32_t *)0xE000EDFCU)

#define PIN_MARKER_CPU   (1U << 0)  // PA0
#define PIN_MARKER_ANLG  (1U << 1)  // PA1
#define PIN_LOAD_SWITCH  (1U << 2)  // PA2

// Структура збережених даних у Retention RAM (SRAM2 / Backup SRAM)
typedef struct {
    uint32_t boot_magic;
    uint32_t wake_counter;
    uint16_t adc_history[64];
    uint32_t last_duration_cycles;
} RetentionStorage;

#define RETENTION_RAM_ADDR 0x10000000U
#define RETENTION_MAGIC    0x57414B45U // "WAKE"

static RetentionStorage *const g_retention = (RetentionStorage *)RETENTION_RAM_ADDR;

static inline void dwt_init(void) {
    CoreDebug_DEMCR |= (1U << 24); // DEMCR_TRCENA
    DWT_CTRL |= (1U << 0);        // DWT_CTRL_CYCCNTENA
}

static inline void marker_cpu_high(void) {
    GPIOA_BSRR = PIN_MARKER_CPU;
}

static inline void marker_cpu_low(void) {
    GPIOA_BSRR = (PIN_MARKER_CPU << 16);
}

static inline void sensor_power_on(void) {
    GPIOA_BSRR = PIN_LOAD_SWITCH | PIN_MARKER_ANLG;
}

static inline void sensor_power_off(void) {
    GPIOA_BSRR = (PIN_LOAD_SWITCH << 16) | (PIN_MARKER_ANLG << 16);
}

// Швидкий замір АЦП без повторного повного калібрування
static uint16_t perform_fast_adc_measurement(void) {
    // Імітація вибірки 16 семплів зі стабілізованого каналу
    volatile uint32_t sum = 0;
    for (int i = 0; i < 16; ++i) {
        sum += (2048U + (uint32_t)(i * 3));
    }
    return (uint16_t)(sum >> 4);
}

void fast_wakeup_sequence(void) {
    // 1. Перший машинний такт: підняти маркер активності CPU
    marker_cpu_high();
    
    // Запуск лічильника циклів DWT для точного виміру
    DWT_CYCCNT = 0;
    
    // 2. Перевірка цілісності Retention RAM
    if (g_retention->boot_magic != RETENTION_MAGIC) {
        g_retention->boot_magic = RETENTION_MAGIC;
        g_retention->wake_counter = 0;
    }
    
    // 3. Комутація живлення давача
    sensor_power_on();
    
    // 4. Очікування стабілізації аналогової шини (наприклад, 120 мкс на 16 МГц MSI = 1920 тактів)
    uint32_t start_tick = DWT_CYCCNT;
    while ((DWT_CYCCNT - start_tick) < 1920U) {
        // Очікування завершення перехідного процесу
    }
    
    // 5. Виконання швидкої вибірки АЦП
    uint16_t sample = perform_fast_adc_measurement();
    
    // 6. Збереження результату у збережену пам'ять
    uint32_t idx = g_retention->wake_counter % 64U;
    g_retention->adc_history[idx] = sample;
    g_retention->wake_counter++;
    
    // Зняття живлення з давача
    sensor_power_off();
    
    // Фіксація тривалості циклу в тактах
    g_retention->last_duration_cycles = DWT_CYCCNT;
    
    // 7. Опускання маркерного виводу безпосередньо перед засинанням
    marker_cpu_low();
    
    // Очищення прапорця пробудження та перехід у глибокий сон (Stop 2)
    PWR_SCR = (1U << 0); // Clear WUF (Wakeup Flag)
    PWR_CR1 |= (1U << 14); // LPMS = Stop 2 Mode
    
    __asm volatile ("wfi");
}
