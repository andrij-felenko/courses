#include <stdint.h>
#include <stdbool.h>

/* Базові адреси периферії та системного контролера */
#define RCC_BASE              (0x40023800UL)
#define TIM2_BASE             (0x40000000UL)
#define DBGMCU_BASE           (0xE0042000UL)

/* Зміщення регістрів блоку тактування RCC */
#define RCC_APB1ENR_OFFSET    (0x40UL)
#define RCC_APB1ENR_TIM2EN    (1UL << 0)   /* Біт тактування таймера TIM2 */

/* Бітові маски таймера TIM2 */
#define TIM_CR1_CEN           (1UL << 0)   /* Counter Enable: увімкнення лічильника */
#define TIM_DIER_UIE          (1UL << 0)   /* Update Interrupt Enable */
#define TIM_SR_UIF           (1UL << 0)   /* Update Interrupt Flag (W1C / rc_w0) */

/* Структура регістрової карти таймера за Reference Manual */
typedef struct {
    volatile uint32_t CR1;    /* +0x00: Control Register 1 */
    volatile uint32_t CR2;    /* +0x04: Control Register 2 */
    volatile uint32_t SMCR;   /* +0x08: Slave Mode Control */
    volatile uint32_t DIER;   /* +0x0C: DMA/Interrupt Enable */
    volatile uint32_t SR;     /* +0x10: Status Register (W1C flags) */
    volatile uint32_t EGR;    /* +0x14: Event Generation */
    volatile uint32_t CCMR1;  /* +0x18: Capture/Compare Mode 1 */
    volatile uint32_t CCMR2;  /* +0x1C: Capture/Compare Mode 2 */
    volatile uint32_t CCER;   /* +0x20: Capture/Compare Enable */
    volatile uint32_t CNT;    /* +0x24: Counter Register */
    volatile uint32_t PSC;    /* +0x28: Prescaler Register */
    volatile uint32_t ARR;    /* +0x2C: Auto-Reload Register */
} TimerRegisters;

typedef struct {
    volatile uint32_t IDCODE; /* +0x00: Device ID & Revision */
} DbgMcuRegisters;

#define TIM2     ((TimerRegisters *)TIM2_BASE)
#define DBGMCU   ((DbgMcuRegisters *)DBGMCU_BASE)
#define RCC_REG(offset) (*(volatile uint32_t *)(RCC_BASE + (offset)))

/* Перевірка ревізії: ревізія Rev A (0x1000) потребує програмного оновлення EGR */
static inline bool is_silicon_rev_a(void) {
    return ((DBGMCU->IDCODE >> 16) & 0xFFFFU) == 0x1000U;
}

/* Ініціалізація таймера на 1000 спрацьовувань на секунду (1 кГц) */
void timer2_init_1khz(uint32_t timer_clock_hz) {
    /* 1. Подача тактування на шину APB1 (Clock Gating) */
    RCC_REG(RCC_APB1ENR_OFFSET) |= RCC_APB1ENR_TIM2EN;

    /* 2. Налаштування дільника (PSC) та порогу переповнення (ARR) ДО увімкнення */
    TIM2->CR1 = 0; /* Гарантуємо, що лічильник вимкнений */
    TIM2->PSC = (timer_clock_hz / 1000000UL) - 1UL; /* Рахуємо мікросекунди */
    TIM2->ARR = 1000UL - 1UL;                       /* 1000 мкс = 1 мс (1 кГц) */

    /* 3. Апаратний обхід Errata Sheet для ревізії Rev A:
     * У ревізії Rev A значення предільника не завантажується автоматично в буфер */
    if (is_silicon_rev_a()) {
        TIM2->EGR = (1UL << 0); /* Примусова генерація події Update Event (UG) */
        TIM2->SR = 0;           /* Очищення прапорця UIF після генерації UG */
    }

    /* 4. Дозвіл переривання за переповненням */
    TIM2->DIER |= TIM_DIER_UIE;

    /* 5. Запуск рахунку */
    TIM2->CR1 |= TIM_CR1_CEN;
}

/* Обробник переривання таймера TIM2 */
void TIM2_IRQHandler(void) {
    /* Перевіряємо апаратний прапорець переповнення лічильника */
    if (TIM2->SR & TIM_SR_UIF) {
        /* Атомарне скидання прапорця через W1C (запис 0 у біт UIF для старих контролерів) */
        TIM2->SR = ~TIM_SR_UIF;

        /* Бар'єр даних проти повторного хибного виклику переривання на Cortex-M4 */
        __asm__ volatile ("dsb" ::: "memory");

        /* Корисна робота обробника */
    }
}
