#include <stdint.h>
#include <stdbool.h>

/* Базові адреси регістрів ядра ARM Cortex-M для роботи з DWT */
#define CORE_DEMCR           (*((volatile uint32_t*)0xE000EDFC))
#define CORE_DEMCR_TRCENA    (1UL << 24)
#define DWT_CTRL             (*((volatile uint32_t*)0xE0001000))
#define DWT_CTRL_CYCCNTENA   (1UL << 0)
#define DWT_CYCCNT           (*((volatile uint32_t*)0xE0001004))

/* Адреси керування GPIO для діагностичного піна (приклад для порту GPIOB Pin 5) */
#define GPIOB_BSRR           (*((volatile uint32_t*)0x40020418))
#define DIAG_PIN_SET         (1UL << 5)
#define DIAG_PIN_RESET       (1UL << (5 + 16))

/* Граничний поріг допустимої тривалості критичної секції (у тактах процесора) */
#define MAX_ALLOWED_CRITICAL_CYCLES 840 /* 5 мікросекунд при частоті ядра 168 МГц */

typedef struct {
    uint32_t max_hold_cycles;
    uint32_t total_violations;
    uint32_t last_violation_cycles;
} critical_diagnostics_t;

static volatile critical_diagnostics_t g_diag_stats = {0, 0, 0};

/* Ініціалізація лічильника DWT для високоточного профілювання */
void critical_diagnostics_init(void) {
    /* Дозвіл трасування та налагоджувальних блоків ядра */
    CORE_DEMCR |= CORE_DEMCR_TRCENA;
    /* Скидання лічильника циклів */
    DWT_CYCCNT = 0;
    /* Увімкнення лічильника CYCCNT */
    DWT_CTRL |= DWT_CTRL_CYCCNTENA;
}

/* Діагностичний вхід у критичну секцію */
static inline uint32_t monitored_critical_enter(void) {
    /* Підняття діагностичного виводу GPIO у високий стан (1 такт) */
    GPIOB_BSRR = DIAG_PIN_SET;

    uint32_t prev_basepri;
    __asm__ volatile ("" ::: "memory");
    __asm__ volatile ("mrs %0, basepri" : "=r" (prev_basepri));
    __asm__ volatile ("msr basepri, %0" :: "r" (0x50) : "memory");
    __asm__ volatile ("dsb 0xF" ::: "memory");
    __asm__ volatile ("isb 0xF" ::: "memory");
    __asm__ volatile ("" ::: "memory");

    /* Захоплення початкового значення лічильника тактів */
    return prev_basepri;
}

/* Діагностичний вихід із перевіркою тривалості */
static inline void monitored_critical_exit(uint32_t prev_basepri, uint32_t start_cycles) {
    uint32_t end_cycles = DWT_CYCCNT;

    __asm__ volatile ("" ::: "memory");
    __asm__ volatile ("dsb 0xF" ::: "memory");
    __asm__ volatile ("msr basepri, %0" :: "r" (prev_basepri) : "memory");
    __asm__ volatile ("isb 0xF" ::: "memory");
    __asm__ volatile ("" ::: "memory");

    /* Опускання діагностичного виводу GPIO у низький стан (1 такт) */
    GPIOB_BSRR = DIAG_PIN_RESET;

    /* Розрахунок часу утримання критичної секції з урахуванням переповнення */
    uint32_t elapsed = end_cycles - start_cycles;

    if (elapsed > g_diag_stats.max_hold_cycles) {
        g_diag_stats.max_hold_cycles = elapsed;
    }

    if (elapsed > MAX_ALLOWED_CRITICAL_CYCLES) {
        g_diag_stats.total_violations++;
        g_diag_stats.last_violation_cycles = elapsed;
        /* Точка спрацювання апаратного переривання налагоджувача для пошуку винуватця */
        __asm__ volatile ("bkpt #0");
    }
}
