#include <stdint.h>

/* Регістри трасування Cortex-M (CoreDebug та DWT) */
#define CoreDebug_DEMCR (*(volatile uint32_t *)0xE000EDFCU)
#define DWT_CTRL        (*(volatile uint32_t *)0xE0001000U)
#define DWT_CYCCNT      (*(volatile uint32_t *)0xE0001004U)

#define NVIC_ISPR0      (*(volatile uint32_t *)0xE000E200U)
#define NVIC_ISER0      (*(volatile uint32_t *)0xE000E100U)

static volatile uint32_t g_t_start = 0;
static volatile uint32_t g_t_isr = 0;
static volatile uint32_t g_measured_latency = 0;
static volatile uint32_t g_dwt_overhead = 0;

void dwt_init(void) {
    /* 1. Дозволяємо роботу блоку трасування (біт TRCENA = 24 в DEMCR) */
    CoreDebug_DEMCR |= (1U << 24);

    /* 2. Скидаємо лічильник циклів у 0 */
    DWT_CYCCNT = 0;

    /* 3. Вмикаємо лічильник циклів (біт CYCCNTENA = 0 в DWT_CTRL) */
    DWT_CTRL |= (1U << 0);

    /* Дозволяємо переривання EXTI0 (номер 6) */
    NVIC_ISER0 = (1U << 6);

    /* Калібрування накладних витрат самого читання DWT */
    uint32_t t1 = DWT_CYCCNT;
    uint32_t t2 = DWT_CYCCNT;
    g_dwt_overhead = t2 - t1;
}

void measure_software_latency(void) {
    /* Захоплюємо стартовий час і негайно виставляємо Pending у NVIC */
    g_t_start = DWT_CYCCNT;
    NVIC_ISPR0 = (1U << 6);

    /* Бар'єр пам'яті для гарантії порядку запису */
    __asm volatile("dsb" ::: "memory");
    __asm volatile("isb" ::: "memory");
}

/* Обробник переривання для DWT-тесту */
void EXTI0_IRQHandler_DWT(void) {
    /* Перший крок: негайно зафіксувати такти */
    g_t_isr = DWT_CYCCNT;

    /* Обчислення чистої різниці тактів з урахуванням накладних витрат */
    g_measured_latency = (g_t_isr - g_t_start) - g_dwt_overhead;
}
