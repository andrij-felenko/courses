#include <stdint.h>
#include <stdbool.h>

/* Базові структури регістрів для nRF52 PPI (CMSIS-подібні) */
#define PPI_CH_TIMER_TO_GPIO   0U
#define PPI_FORK_ADC           1U

typedef struct {
    volatile uint32_t TASKS_OUT[8];
    volatile uint32_t EVENTS_IN[8];
    volatile uint32_t CONFIG[8];
} NRF_GPIOTE_Type;

typedef struct {
    volatile uint32_t TASKS_START;
    volatile uint32_t TASKS_STOP;
    volatile uint32_t TASKS_CLEAR;
    volatile uint32_t EVENTS_COMPARE[4];
    volatile uint32_t SHORTS;
    volatile uint32_t CC[4];
} NRF_TIMER_Type;

typedef struct {
    volatile uint32_t TASKS_SAMPLE;
} NRF_SAADC_Type;

typedef struct {
    struct {
        volatile uint32_t EEP;      /* Event End Point (адреса події-джерела) */
        volatile uint32_t TEP;      /* Task End Point (адреса задачі-споживача) */
    } CH[32];
    volatile uint32_t CHEN;         /* Channel Enable */
    volatile uint32_t CHENSET;      /* Channel Enable Set */
    volatile uint32_t CHENCLR;      /* Channel Enable Clear */
    struct {
        volatile uint32_t TEP;      /* Fork Task End Point */
    } FORK[32];
} NRF_PPI_Type;

extern NRF_GPIOTE_Type * const NRF_GPIOTE_BASE;
extern NRF_TIMER_Type  * const NRF_TIMER1_BASE;
extern NRF_SAADC_Type  * const NRF_SAADC_BASE;
extern NRF_PPI_Type    * const NRF_PPI_BASE;

void ppi_hardware_pipe_init(void) {
    /* 1. Налаштування таймера на період 500 мкс (при частоті 16 МГц: 8000 тактів) */
    NRF_TIMER1_BASE->CC[0] = 8000;
    NRF_TIMER1_BASE->SHORTS = (1UL << 0); /* COMPARE0_CLEAR: автоскидання лічильника */

    /* 2. Налаштування модуля GPIOTE: перемикання (Toggle) виводу при виконанні задачі */
    /* MODE=Task (3), POLARITY=Toggle (3), PSEL=13 (вивід P0.13) */
    NRF_GPIOTE_BASE->CONFIG[0] = (3UL << 0) | (13UL << 8) | (3UL << 16);

    /* 3. Конфігурація централізованого каналу PPI */
    /* Джерело (EEP): подія порівняння таймера */
    NRF_PPI_BASE->CH[PPI_CH_TIMER_TO_GPIO].EEP = (uint32_t)&NRF_TIMER1_BASE->EVENTS_COMPARE[0];
    
    /* Основний споживач (TEP): задача перемикання ніжки GPIOTE */
    NRF_PPI_BASE->CH[PPI_CH_TIMER_TO_GPIO].TEP = (uint32_t)&NRF_GPIOTE_BASE->TASKS_OUT[0];

    /* Додатковий споживач через FORK: запуск вибірки АЦП */
    NRF_PPI_BASE->FORK[PPI_CH_TIMER_TO_GPIO].TEP = (uint32_t)&NRF_SAADC_BASE->TASKS_SAMPLE;

    /* 4. Активація каналу PPI */
    NRF_PPI_BASE->CHENSET = (1UL << PPI_CH_TIMER_TO_GPIO);

    /* 5. Старт таймера - далі конвеєр працює повністю апаратно */
    NRF_TIMER1_BASE->TASKS_START = 1;
}
