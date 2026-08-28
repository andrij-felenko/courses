#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

// ── Перелік підтримуваних периферійних модулів ──────────────────────────────
typedef enum {
    PERIPH_GPIOA = 0,
    PERIPH_GPIOB,
    PERIPH_GPIOC,
    PERIPH_DMA1,
    PERIPH_DMA2,
    PERIPH_USART1,
    PERIPH_USART2,
    PERIPH_I2C1,
    PERIPH_SPI1,
    PERIPH_TIM2,
    PERIPH_ADC1,
    PERIPH_MAX_COUNT
} periph_id_t;

// ── Шинні домени мікроконтролера ─────────────────────────────────────────────
typedef enum {
    BUS_DOMAIN_AHB1 = 0,
    BUS_DOMAIN_AHB2,
    BUS_DOMAIN_APB1,
    BUS_DOMAIN_APB2,
    BUS_DOMAIN_COUNT
} bus_domain_t;

// ── Статуси повернення операцій ──────────────────────────────────────────────
typedef enum {
    CLOCK_STATUS_OK = 0,
    CLOCK_STATUS_INVALID_ARG,
    CLOCK_STATUS_REF_OVERFLOW,
    CLOCK_STATUS_REF_UNDERFLOW,
    CLOCK_STATUS_HW_TIMEOUT
} clock_status_t;

// ── Апаратна структура симулятора RCC ─────────────────────────────────────────
typedef struct {
    volatile uint32_t AHB1ENR;
    volatile uint32_t AHB2ENR;
    volatile uint32_t APB1ENR;
    volatile uint32_t APB2ENR;
    volatile uint32_t AHB1LPENR;
    volatile uint32_t APB1LPENR;
    volatile uint32_t APB2LPENR;
    volatile uint32_t AHB1RSTR;
    volatile uint32_t APB1RSTR;
    volatile uint32_t APB2RSTR;
} rcc_registers_t;

// Глобальний екземпляр регістрів (у реальному чипі: (rcc_registers_t*)0x40023800)
static rcc_registers_t g_hw_rcc;

// ── Опис залежностей периферії ───────────────────────────────────────────────
#define MAX_DEPENDENCIES 2

typedef struct {
    bus_domain_t        domain;          // Домен шини (AHB1/APB1/APB2)
    volatile uint32_t  *enr_register;    // Регістр увімкнення тактування
    volatile uint32_t  *lpenr_register;  // Регістр тактування в режимі сну
    volatile uint32_t  *rstr_register;   // Регістр апаратного скидання
    uint32_t            mask;            // Бітова маска модуля
    periph_id_t         deps[MAX_DEPENDENCIES]; // Залежні вузли (напр. GPIO)
    uint8_t             dep_count;       // Кількість залежностей
    uint32_t            dynamic_current_ua; // Оцінка споживання струму (мкА)
} periph_metadata_t;

// ── Таблиця дескрипторів периферії (зберігається у Flash-пам'яті) ─────────────
static const periph_metadata_t g_periph_meta[PERIPH_MAX_COUNT] = {
    [PERIPH_GPIOA] = {
        .domain = BUS_DOMAIN_AHB1,
        .enr_register = &g_hw_rcc.AHB1ENR,
        .lpenr_register = &g_hw_rcc.AHB1LPENR,
        .rstr_register = &g_hw_rcc.AHB1RSTR,
        .mask = (1U << 0),
        .dep_count = 0,
        .dynamic_current_ua = 250
    },
    [PERIPH_GPIOB] = {
        .domain = BUS_DOMAIN_AHB1,
        .enr_register = &g_hw_rcc.AHB1ENR,
        .lpenr_register = &g_hw_rcc.AHB1LPENR,
        .rstr_register = &g_hw_rcc.AHB1RSTR,
        .mask = (1U << 1),
        .dep_count = 0,
        .dynamic_current_ua = 250
    },
    [PERIPH_GPIOC] = {
        .domain = BUS_DOMAIN_AHB1,
        .enr_register = &g_hw_rcc.AHB1ENR,
        .lpenr_register = &g_hw_rcc.AHB1LPENR,
        .rstr_register = &g_hw_rcc.AHB1RSTR,
        .mask = (1U << 2),
        .dep_count = 0,
        .dynamic_current_ua = 250
    },
    [PERIPH_DMA1] = {
        .domain = BUS_DOMAIN_AHB1,
        .enr_register = &g_hw_rcc.AHB1ENR,
        .lpenr_register = &g_hw_rcc.AHB1LPENR,
        .rstr_register = &g_hw_rcc.AHB1RSTR,
        .mask = (1U << 21),
        .dep_count = 0,
        .dynamic_current_ua = 1200
    },
    [PERIPH_DMA2] = {
        .domain = BUS_DOMAIN_AHB1,
        .enr_register = &g_hw_rcc.AHB1ENR,
        .lpenr_register = &g_hw_rcc.AHB1LPENR,
        .rstr_register = &g_hw_rcc.AHB1RSTR,
        .mask = (1U << 22),
        .dep_count = 0,
        .dynamic_current_ua = 1200
    },
    [PERIPH_USART1] = {
        .domain = BUS_DOMAIN_APB2,
        .enr_register = &g_hw_rcc.APB2ENR,
        .lpenr_register = &g_hw_rcc.APB2LPENR,
        .rstr_register = &g_hw_rcc.APB2RSTR,
        .mask = (1U << 4),
        .deps = { PERIPH_GPIOA },
        .dep_count = 1,
        .dynamic_current_ua = 850
    },
    [PERIPH_USART2] = {
        .domain = BUS_DOMAIN_APB1,
        .enr_register = &g_hw_rcc.APB1ENR,
        .lpenr_register = &g_hw_rcc.APB1LPENR,
        .rstr_register = &g_hw_rcc.APB1RSTR,
        .mask = (1U << 17),
        .deps = { PERIPH_GPIOA },
        .dep_count = 1,
        .dynamic_current_ua = 600
    },
    [PERIPH_I2C1] = {
        .domain = BUS_DOMAIN_APB1,
        .enr_register = &g_hw_rcc.APB1ENR,
        .lpenr_register = &g_hw_rcc.APB1LPENR,
        .rstr_register = &g_hw_rcc.APB1RSTR,
        .mask = (1U << 21),
        .deps = { PERIPH_GPIOB },
        .dep_count = 1,
        .dynamic_current_ua = 450
    },
    [PERIPH_SPI1] = {
        .domain = BUS_DOMAIN_APB2,
        .enr_register = &g_hw_rcc.APB2ENR,
        .lpenr_register = &g_hw_rcc.APB2LPENR,
        .rstr_register = &g_hw_rcc.APB2RSTR,
        .mask = (1U << 12),
        .deps = { PERIPH_GPIOA, PERIPH_DMA2 },
        .dep_count = 2,
        .dynamic_current_ua = 1100
    },
    [PERIPH_TIM2] = {
        .domain = BUS_DOMAIN_APB1,
        .enr_register = &g_hw_rcc.APB1ENR,
        .lpenr_register = &g_hw_rcc.APB1LPENR,
        .rstr_register = &g_hw_rcc.APB1RSTR,
        .mask = (1U << 0),
        .dep_count = 0,
        .dynamic_current_ua = 700
    },
    [PERIPH_ADC1] = {
        .domain = BUS_DOMAIN_APB2,
        .enr_register = &g_hw_rcc.APB2ENR,
        .lpenr_register = &g_hw_rcc.APB2LPENR,
        .rstr_register = &g_hw_rcc.APB2RSTR,
        .mask = (1U << 8),
        .deps = { PERIPH_GPIOA },
        .dep_count = 1,
        .dynamic_current_ua = 1800
    }
};

// ── Внутрішній динамічний стан диспетчера ────────────────────────────────────
typedef struct {
    uint16_t ref_counts[PERIPH_MAX_COUNT];      // Лічильники посилань модулів
    uint16_t domain_active_count[BUS_DOMAIN_COUNT]; // Кількість активних модулів на шині
    uint64_t total_active_cycles[PERIPH_MAX_COUNT]; // Час активності (умовні такти)
    uint32_t lock_nesting;                      // Рівень вкладеності критичної секції
} clock_manager_state_t;

static clock_manager_state_t g_clk_state;

// ── Апаратні бар'єри та критичні секції ──────────────────────────────────────
static inline void clock_enter_critical(void) {
    // В реальній системі: __disable_irq() або taskENTER_CRITICAL()
    g_clk_state.lock_nesting++;
}

static inline void clock_exit_critical(void) {
    // В реальній системі: __enable_irq() або taskEXIT_CRITICAL()
    if (g_clk_state.lock_nesting > 0) {
        g_clk_state.lock_nesting--;
    }
}

static inline void clock_hw_sync_barrier(volatile uint32_t *reg) {
    // 1. Фіктивне читання (Dummy Read) для очікування шини
    volatile uint32_t dummy = *reg;
    (void)dummy;

    // 2. Архітектурний бар'єр даних (у Cortex-M: __DSB())
    __asm volatile("" ::: "memory");
}

// ── Ініціалізація диспетчера ────────────────────────────────────────────────
void clock_manager_init(void) {
    clock_enter_critical();
    memset(&g_clk_state, 0, sizeof(g_clk_state));
    memset(&g_hw_rcc, 0, sizeof(g_hw_rcc));
    clock_exit_critical();
}

// ── Внутрішня функція фізичного увімкнення модуля ────────────────────────────
static void clock_hw_enable_node(periph_id_t id) {
    const periph_metadata_t *meta = &g_periph_meta[id];
    
    // Ввімкнення тактування
    *meta->enr_register |= meta->mask;
    // Дозвіл тактування в режимі низького споживання за замовчуванням
    if (meta->lpenr_register != NULL) {
        *meta->lpenr_register |= meta->mask;
    }
    // Апаратний бар'єр затримки
    clock_hw_sync_barrier(meta->enr_register);
    
    // Оновлення лічильника домену
    g_clk_state.domain_active_count[meta->domain]++;
}

// ── Внутрішня функція фізичного вимкнення модуля ────────────────────────────
static void clock_hw_disable_node(periph_id_t id) {
    const periph_metadata_t *meta = &g_periph_meta[id];
    
    // Вимкнення тактування
    *meta->enr_register &= ~meta->mask;
    if (meta->lpenr_register != NULL) {
        *meta->lpenr_register &= ~meta->mask;
    }
    // Апаратний бар'єр затримки
    clock_hw_sync_barrier(meta->enr_register);
    
    // Оновлення лічильника домену
    if (g_clk_state.domain_active_count[meta->domain] > 0) {
        g_clk_state.domain_active_count[meta->domain]--;
    }
}

// ── Захоплення тактування периферійного модуля ──────────────────────────────
clock_status_t clock_manager_acquire(periph_id_t id) {
    if (id >= PERIPH_MAX_COUNT) {
        return CLOCK_STATUS_INVALID_ARG;
    }

    clock_enter_critical();
    const periph_metadata_t *meta = &g_periph_meta[id];

    // 1. Рекурсивне захоплення залежностей
    for (uint8_t i = 0; i < meta->dep_count; ++i) {
        clock_status_t dep_res = clock_manager_acquire(meta->deps[i]);
        if (dep_res != CLOCK_STATUS_OK) {
            // Відкат уже захоплених залежностей при помилці
            for (uint8_t j = 0; j < i; ++j) {
                clock_manager_release(meta->deps[j]);
            }
            clock_exit_critical();
            return dep_res;
        }
    }

    // 2. Перевірка переповнення лічильника
    if (g_clk_state.ref_counts[id] == UINT16_MAX) {
        // Відкат залежностей
        for (uint8_t i = 0; i < meta->dep_count; ++i) {
            clock_manager_release(meta->deps[i]);
        }
        clock_exit_critical();
        return CLOCK_STATUS_REF_OVERFLOW;
    }

    // 3. Фізичне ввімкнення при переході 0 -> 1
    if (g_clk_state.ref_counts[id] == 0) {
        clock_hw_enable_node(id);
    }

    g_clk_state.ref_counts[id]++;
    clock_exit_critical();
    return CLOCK_STATUS_OK;
}

// ── Звільнення тактування периферійного модуля ──────────────────────────────
clock_status_t clock_manager_release(periph_id_t id) {
    if (id >= PERIPH_MAX_COUNT) {
        return CLOCK_STATUS_INVALID_ARG;
    }

    clock_enter_critical();
    if (g_clk_state.ref_counts[id] == 0) {
        clock_exit_critical();
        return CLOCK_STATUS_REF_UNDERFLOW;
    }

    g_clk_state.ref_counts[id]--;

    // Фізичне вимкнення при переході 1 -> 0
    if (g_clk_state.ref_counts[id] == 0) {
        clock_hw_disable_node(id);
    }

    // Рекурсивне звільнення залежностей
    const periph_metadata_t *meta = &g_periph_meta[id];
    for (uint8_t i = 0; i < meta->dep_count; ++i) {
        clock_manager_release(meta->deps[i]);
    }

    clock_exit_critical();
    return CLOCK_STATUS_OK;
}

// ── Апаратне скидання модуля через диспетчер ────────────────────────────────
clock_status_t clock_manager_reset_module(periph_id_t id) {
    if (id >= PERIPH_MAX_COUNT) {
        return CLOCK_STATUS_INVALID_ARG;
    }

    clock_enter_critical();
    const periph_metadata_t *meta = &g_periph_meta[id];
    if (meta->rstr_register == NULL) {
        clock_exit_critical();
        return CLOCK_STATUS_INVALID_ARG;
    }

    // Встановлення біта скидання
    *meta->rstr_register |= meta->mask;
    clock_hw_sync_barrier(meta->rstr_register);

    // Коротка затримка стабілізації
    for (volatile int i = 0; i < 32; ++i) {
        __asm volatile("nop");
    }

    // Зняття біта скидання
    *meta->rstr_register &= ~meta->mask;
    clock_hw_sync_barrier(meta->rstr_register);

    clock_exit_critical();
    return CLOCK_STATUS_OK;
}

// ── Отримання кількості активних модулів на шині ─────────────────────────────
uint16_t clock_manager_get_bus_activity(bus_domain_t domain) {
    if (domain >= BUS_DOMAIN_COUNT) return 0;
    return g_clk_state.domain_active_count[domain];
}

// ── Перевірка активності конкретного модуля ─────────────────────────────────
bool clock_manager_is_enabled(periph_id_t id) {
    if (id >= PERIPH_MAX_COUNT) return false;
    return g_clk_state.ref_counts[id] > 0;
}
