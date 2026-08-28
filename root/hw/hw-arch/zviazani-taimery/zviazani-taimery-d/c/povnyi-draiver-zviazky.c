#include <stdint.h>
#include <stdbool.h>

/* Базові адреси периферійних таймерів STM32 (шина APB1 / APB2) */
#define TIM1_BASE_ADDR   0x40010000U
#define TIM2_BASE_ADDR   0x40000000U
#define TIM3_BASE_ADDR   0x40000400U

/* Структура регістрів таймера загального призначення */
typedef struct {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SMCR;
    volatile uint32_t DIER;
    volatile uint32_t SR;
    volatile uint32_t EGR;
    volatile uint32_t CCMR1;
    volatile uint32_t CCMR2;
    volatile uint32_t CCER;
    volatile uint32_t CNT;
    volatile uint32_t PSC;
    volatile uint32_t ARR;
    volatile uint32_t RCR;
    volatile uint32_t CCR1;
    volatile uint32_t CCR2;
    volatile uint32_t CCR3;
    volatile uint32_t CCR4;
    volatile uint32_t BDTR;
    volatile uint32_t DCR;
    volatile uint32_t DMAR;
} timer_regs_t;

#define TIM1_REGS ((timer_regs_t *)TIM1_BASE_ADDR)
#define TIM2_REGS ((timer_regs_t *)TIM2_BASE_ADDR)
#define TIM3_REGS ((timer_regs_t *)TIM3_BASE_ADDR)

/* Бітові маски керування */
#define TIM_CR1_CEN_BIT        (1U << 0)
#define TIM_CR1_ARPE_BIT       (1U << 7)
#define TIM_EGR_UG_BIT         (1U << 0)

/* Джерела тригера майстра (CR2.MMS) */
typedef enum {
    TIMER_TRGO_SRC_RESET   = 0x00U,
    TIMER_TRGO_SRC_ENABLE  = 0x01U,
    TIMER_TRGO_SRC_UPDATE  = 0x02U,
    TIMER_TRGO_SRC_CC1_PULSE = 0x03U,
    TIMER_TRGO_SRC_OC1REF  = 0x04U,
    TIMER_TRGO_SRC_OC2REF  = 0x05U,
    TIMER_TRGO_SRC_OC3REF  = 0x06U,
    TIMER_TRGO_SRC_OC4REF  = 0x07U
} timer_trgo_src_t;

/* Вхідні тригерні лінії слейва (SMCR.TS) */
typedef enum {
    TIMER_TRGI_SEL_ITR0    = 0x00U,
    TIMER_TRGI_SEL_ITR1    = 0x01U,
    TIMER_TRGI_SEL_ITR2    = 0x02U,
    TIMER_TRGI_SEL_ITR3    = 0x03U,
    TIMER_TRGI_SEL_TI1F_ED = 0x04U,
    TIMER_TRGI_SEL_TI1FP1  = 0x05U,
    TIMER_TRGI_SEL_TI2FP2  = 0x06U,
    TIMER_TRGI_SEL_ETRF    = 0x07U
} timer_trgi_sel_t;

/* Режими роботи слейв-таймера (SMCR.SMS) */
typedef enum {
    TIMER_SLAVE_MODE_DISABLED   = 0x00U,
    TIMER_SLAVE_MODE_RESET      = 0x04U,
    TIMER_SLAVE_MODE_GATED      = 0x05U,
    TIMER_SLAVE_MODE_TRIGGER    = 0x06U,
    TIMER_SLAVE_MODE_EXT_CLOCK1 = 0x07U
} timer_slave_mode_t;

/* Ініціалізація майстер-таймера */
void timer_master_config(timer_regs_t *timer, uint16_t prescaler, uint16_t auto_reload, timer_trgo_src_t trgo_source) {
    timer->CR1 &= ~TIM_CR1_CEN_BIT; // Зупинити лічильник перед налаштуванням
    timer->PSC = prescaler;
    timer->ARR = auto_reload;

    /* Налаштування бітів MMS[2:0] у регістрі CR2 */
    uint32_t cr2_val = timer->CR2;
    cr2_val &= ~(0x07U << 4);
    cr2_val |= ((uint32_t)trgo_source & 0x07U) << 4;
    timer->CR2 = cr2_val;

    timer->EGR |= TIM_EGR_UG_BIT; // Перезавантажити тіньові регістри
}

/* Ініціалізація підлеглого таймера (Slave) */
void timer_slave_config(timer_regs_t *timer, uint16_t prescaler, uint16_t auto_reload,
                        timer_trgi_sel_t trigger_input, timer_slave_mode_t slave_mode) {
    timer->CR1 &= ~TIM_CR1_CEN_BIT;
    timer->PSC = prescaler;
    timer->ARR = auto_reload;

    /* Налаштування бітів TS[2:0] та SMS[2:0] у регістрі SMCR */
    uint32_t smcr_val = timer->SMCR;
    smcr_val &= ~((0x07U << 4) | 0x07U);
    smcr_val |= (((uint32_t)trigger_input & 0x07U) << 4);
    smcr_val |= ((uint32_t)slave_mode & 0x07U);
    timer->SMCR = smcr_val;

    timer->EGR |= TIM_EGR_UG_BIT;
}

/* Побудова 32-бітного лічильника з двох 16-бітних таймерів (TIM2 Master -> TIM3 Slave) */
void timer_cascade_32bit_init(void) {
    /* TIM2: Майстер молодших 16 біт (рахує на повній швидкості, TRGO = Update Event) */
    timer_master_config(TIM2_REGS, 0, 0xFFFFU, TIMER_TRGO_SRC_UPDATE);

    /* TIM3: Слейв старших 16 біт (вхід ITR1, такт від переповнення майстра) */
    timer_slave_config(TIM3_REGS, 0, 0xFFFFU, TIMER_TRGI_SEL_ITR1, TIMER_SLAVE_MODE_EXT_CLOCK1);

    /* Очищення лічильників */
    TIM2_REGS->CNT = 0;
    TIM3_REGS->CNT = 0;

    /* Запуск слейва, потім запуск майстра */
    TIM3_REGS->CR1 |= TIM_CR1_CEN_BIT;
    TIM2_REGS->CR1 |= TIM_CR1_CEN_BIT;
}

/* Неблокуюче атомарне зчитування 32-бітного каскаду */
uint32_t timer_cascade_32bit_read(void) {
    uint16_t high1;
    uint16_t low;
    uint16_t high2;

    do {
        high1 = (uint16_t)TIM3_REGS->CNT;
        low   = (uint16_t)TIM2_REGS->CNT;
        high2 = (uint16_t)TIM3_REGS->CNT;
    } while (high1 != high2);

    return ((uint32_t)high1 << 16) | (uint32_t)low;
}

/* Конфігурація апаратного частотоміра (секундний строб на TIM2, лічба імпульсів на TIM3) */
void timer_frequency_meter_init(uint32_t apb_clock_hz) {
    /* Розрахунок передільника для формування секундного вікна: база часу 10 кГц */
    uint16_t psc_master = (uint16_t)((apb_clock_hz / 10000U) - 1U);
    uint16_t arr_master = 9999U; // (9999 + 1) / 10000 Гц = 1.000000 с

    /* TIM2 генерує строб тривалості роботи CEN на вихід TRGO */
    timer_master_config(TIM2_REGS, psc_master, arr_master, TIMER_TRGO_SRC_ENABLE);

    /* TIM3 працює в режимі Gated Mode за стробом від ITR1 */
    timer_slave_config(TIM3_REGS, 0, 0xFFFFU, TIMER_TRGI_SEL_ITR1, TIMER_SLAVE_MODE_GATED);

    /* Вхід ETR таймера TIM3 підключається до зовнішнього піна */
    TIM3_REGS->SMCR |= (1U << 14); // ECE: Дозвіл тактування від зовнішнього піна ETR
}
