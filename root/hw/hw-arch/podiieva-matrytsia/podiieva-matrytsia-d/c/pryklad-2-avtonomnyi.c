#include <stdint.h>

/* Структури регістрів STM32G4 DMAMUX */
typedef struct {
    volatile uint32_t CCR[16];   /* Канали конфігурації DMA (0x00..0x3C) */
    volatile uint32_t RGCR[4];   /* Регістри генераторів запитів (0x100..0x10C) */
    volatile uint32_t RGSR;      /* Статус генераторів (0x140) */
    volatile uint32_t RGCFR;     /* Очищення статусу (0x144) */
} DMAMUX_Block;

#define DMAMUX1_BASE_ADDR ((DMAMUX_Block*)0x40020800)

/* Ідентифікатори джерел тригерів для генератора запитів DMAMUX1 */
#define DMAMUX_TRIG_COMP1_OUT   23U
#define DMAMUX_REQ_GEN0_ID      1U

void stm32_dmamux_generator_setup(void) {
    DMAMUX_Block * const dmamux = DMAMUX1_BASE_ADDR;

    /* 1. Налаштування Request Generator 0:
          - SIG_ID = 23 (сигнал від виходу компаратора COMP1_OUT)
          - GPOL = 0b01 (генерація запиту по наростаючому фронту)
          - GNBREQ = 0 (генерувати рівно 1 DMA запит на 1 подію)
          - GE = 1 (активація генератора запитів)
    */
    dmamux->RGCR[0] = (DMAMUX_TRIG_COMP1_OUT << 16) |  /* SIG_ID */
                      (1UL << 17)                   |  /* GPOL (Rising edge) */
                      (0UL << 19)                   |  /* GNBREQ (1 transfer) */
                      (1UL << 16);                     /* GE (Generator Enable) */

    /* 2. Прив'язка Каналу 0 DMA до згенерованого запиту Request Generator 0:
          - DMAREQ_ID = 1 (вхідний запит від Generator 0)
    */
    dmamux->CCR[0] = (DMAMUX_REQ_GEN0_ID & 0x7FUL);
}
