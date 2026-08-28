#include <stdint.h>
#include <stdbool.h>

/* Регістри DWT (Data Watchpoint and Trace) для підрахунку тактів */
#define CORE_DEBUG_DEMCR        (*(volatile uint32_t *)0xE000EDFCU)
#define CORE_DEBUG_DEMCR_TRCENA (1U << 24)

#define DWT_CTRL                (*(volatile uint32_t *)0xE0001000U)
#define DWT_CTRL_CYCCNTENA      (1U << 0)
#define DWT_CYCCNT              (*(volatile uint32_t *)0xE0001004U)

/* Регістр конфігурації Flash */
#define FLASH_ACR               (*(volatile uint32_t *)0x40023C00U)
#define FLASH_ACR_LATENCY_5WS   (5U)
#define FLASH_ACR_PRFTEN        (1U << 8)
#define FLASH_ACR_ICEN          (1U << 9)
#define FLASH_ACR_DCEN          (1U << 10)
#define FLASH_ACR_ICRST         (1U << 11)
#define FLASH_ACR_DCRST         (1U << 12)

/* Символи з Linker Script для релокації .ramfunc */
extern uint32_t _si_ramfunc;
extern uint32_t _sramfunc;
extern uint32_t _eramfunc;

/* Функція копіювання коду в RAM під час стартапу */
void relocate_ramfunc(void) {
    uint32_t *src = &_si_ramfunc;
    uint32_t *dst = &_sramfunc;
    while (dst < &_eramfunc) {
        *dst++ = *src++;
    }
}

/* Ініціалізація апаратного лічильника тактів */
void dwt_init(void) {
    CORE_DEBUG_DEMCR |= CORE_DEBUG_DEMCR_TRCENA;
    DWT_CYCCNT = 0;
    DWT_CTRL |= DWT_CTRL_CYCCNTENA;
}

static inline uint32_t dwt_get_cycles(void) {
    return DWT_CYCCNT;
}

#define ARRAY_SIZE 128
static int32_t test_data_a[ARRAY_SIZE];
static int32_t test_data_b[ARRAY_SIZE];

/* Тестове ядро: скалярне множення та умовне накопичення (Flash) */
__attribute__((noinline))
int32_t compute_kernel_flash(const int32_t *a, const int32_t *b, uint32_t len) {
    int32_t sum = 0;
    for (uint32_t i = 0; i < len; ++i) {
        int32_t prod = a[i] * b[i];
        if (prod > 1000) {
            sum += prod >> 2;
        } else {
            sum -= prod;
        }
    }
    return sum;
}

/* Те саме ядро, скомпільоване для виконання з RAM */
__attribute__((noinline, section(".ramfunc")))
int32_t compute_kernel_ram(const int32_t *a, const int32_t *b, uint32_t len) {
    int32_t sum = 0;
    for (uint32_t i = 0; i < len; ++i) {
        int32_t prod = a[i] * b[i];
        if (prod > 1000) {
            sum += prod >> 2;
        } else {
            sum -= prod;
        }
    }
    return sum;
}

typedef struct {
    uint32_t cycles_raw_flash;
    uint32_t cycles_prefetch;
    uint32_t cycles_art_cache;
    uint32_t cycles_ram;
} benchmark_results_t;

benchmark_results_t run_benchmark(void) {
    benchmark_results_t res;
    volatile int32_t dummy = 0;
    uint32_t t_start, t_end;

    for (uint32_t i = 0; i < ARRAY_SIZE; ++i) {
        test_data_a[i] = (int32_t)(i * 17 + 5);
        test_data_b[i] = (int32_t)(i * 31 - 12);
    }

    /* 1. Flash 5WS: без Prefetch, без кешу */
    FLASH_ACR = FLASH_ACR_LATENCY_5WS;
    t_start = dwt_get_cycles();
    dummy += compute_kernel_flash(test_data_a, test_data_b, ARRAY_SIZE);
    t_end = dwt_get_cycles();
    res.cycles_raw_flash = t_end - t_start;

    /* 2. Flash 5WS: Prefetch ON, Cache OFF */
    FLASH_ACR = FLASH_ACR_LATENCY_5WS | FLASH_ACR_PRFTEN;
    t_start = dwt_get_cycles();
    dummy += compute_kernel_flash(test_data_a, test_data_b, ARRAY_SIZE);
    t_end = dwt_get_cycles();
    res.cycles_prefetch = t_end - t_start;

    /* 3. Flash 5WS: Prefetch ON, I-Cache ON, D-Cache ON (ART) */
    /* Скидаємо та вмикаємо кеші */
    FLASH_ACR = FLASH_ACR_LATENCY_5WS | FLASH_ACR_PRFTEN;
    FLASH_ACR |= (FLASH_ACR_ICRST | FLASH_ACR_DCRST);
    FLASH_ACR &= ~(FLASH_ACR_ICRST | FLASH_ACR_DCRST);
    FLASH_ACR |= (FLASH_ACR_ICEN | FLASH_ACR_DCEN);

    /* Прогрів кешу (1-й запуск) */
    dummy += compute_kernel_flash(test_data_a, test_data_b, ARRAY_SIZE);

    /* Замір швидкодії гарячого кешу */
    t_start = dwt_get_cycles();
    dummy += compute_kernel_flash(test_data_a, test_data_b, ARRAY_SIZE);
    t_end = dwt_get_cycles();
    res.cycles_art_cache = t_end - t_start;

    /* 4. Виконання з RAM (.ramfunc) */
    t_start = dwt_get_cycles();
    dummy += compute_kernel_ram(test_data_a, test_data_b, ARRAY_SIZE);
    t_end = dwt_get_cycles();
    res.cycles_ram = t_end - t_start;

    (void)dummy;
    return res;
}
