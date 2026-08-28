#include <stdint.h>
#include <stdbool.h>

/* Базові структури регістрів для ілюстрації апаратної конфігурації DPPI */
#define DPPI_CH_TRIGGER   0U
#define DPPI_CH_SAMPLE    1U
#define BUFFER_SIZE_WORDS 1024U

/* Умовні вказівники на периферійні блоки nRF (CMSIS-сумісні) */
typedef struct {
    volatile uint32_t TASKS_START;
    volatile uint32_t TASKS_STOP;
    volatile uint32_t EVENTS_UP;
    volatile uint32_t PUBLISH_UP;
} COMP_Regs;

typedef struct {
    volatile uint32_t TASKS_START;
    volatile uint32_t TASKS_STOP;
    volatile uint32_t TASKS_CLEAR;
    volatile uint32_t EVENTS_COMPARE[4];
    volatile uint32_t CC[4];
    volatile uint32_t SHORTS;
    volatile uint32_t SUBSCRIBE_START;
    volatile uint32_t PUBLISH_COMPARE[4];
} TIMER_Regs;

typedef struct {
    volatile uint32_t TASKS_START;
    volatile uint32_t TASKS_SAMPLE;
    volatile uint32_t EVENTS_END;
    volatile uint32_t RESULT_PTR;
    volatile uint32_t RESULT_MAXCNT;
    volatile uint32_t SUBSCRIBE_SAMPLE;
} SAADC_Regs;

typedef struct {
    volatile uint32_t CHEN;
    volatile uint32_t CHENSET;
    volatile uint32_t CHENCLR;
} DPPI_Regs;

/* Зовнішні адреси блоків */
extern COMP_Regs  * const NRF_COMP;
extern TIMER_Regs * const NRF_TIMER0;
extern SAADC_Regs * const NRF_SAADC;
extern DPPI_Regs  * const NRF_DPPI;

/* Буфер даних для EasyDMA у пам'яті SRAM */
static uint16_t adc_dma_buffer[BUFFER_SIZE_WORDS] __attribute__((aligned(4)));

void pipeline_dppi_init(void) {
    /* 1. Налаштування джерела: Компаратор публікує подію перевищення порогу */
    /* Біт 31 (EN) = 1, Біти 0..7 = номер каналу (0) */
    NRF_COMP->PUBLISH_UP = (1UL << 31) | DPPI_CH_TRIGGER;

    /* 2. Налаштування проміжної ланки: Таймер слухає канал 0 та публікує на канал 1 */
    NRF_TIMER0->SUBSCRIBE_START = (1UL << 31) | DPPI_CH_TRIGGER;
    NRF_TIMER0->CC[0] = 160; /* 10 мкс при тактуванні 16 МГц */
    NRF_TIMER0->SHORTS = (1UL << 0); /* Автоскидання COMPARE0 -> CLEAR */
    NRF_TIMER0->PUBLISH_COMPARE[0] = (1UL << 31) | DPPI_CH_SAMPLE;

    /* 3. Налаштування споживача: SAADC підписаний на запуск вибірки з каналу 1 */
    NRF_SAADC->SUBSCRIBE_SAMPLE = (1UL << 31) | DPPI_CH_SAMPLE;
    NRF_SAADC->RESULT_PTR = (uint32_t)adc_dma_buffer;
    NRF_SAADC->RESULT_MAXCNT = BUFFER_SIZE_WORDS;

    /* 4. Активація каналів 0 та 1 у системному комутаторі DPPI */
    NRF_DPPI->CHENSET = (1UL << DPPI_CH_TRIGGER) | (1UL << DPPI_CH_SAMPLE);

    /* 5. Запуск EasyDMA для SAADC та переведення ядра в режим очікування */
    NRF_SAADC->TASKS_START = 1;
}
