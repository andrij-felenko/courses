#include "pwm_driver.h"
#include <stddef.h>

/**
 * @file pwm_driver.c
 * @brief Реалізація програмування регістрів таймера для трифазного комплементарного ШІМ.
 */

/* Екземпляр апаратних регістрів таймера TIM1 (імітація MMIO або фізичні регістри MCU) */
static TIM_TypeDef g_tim1_hardware_registers;
#define TIM1 (&g_tim1_hardware_registers)

/**
 * @brief Обчислення байта конфігурації генератора дед-тайму (BDTR DTG).
 * @param timer_clk_hz Тактова частота таймера (Гц).
 * @param deadtime_ns Бажаний dead-time у наносекундах.
 * @return Значення бітів DTG [7:0].
 */
uint8_t pwm_calculate_dtg(uint32_t timer_clk_hz, uint32_t deadtime_ns) {
    if (timer_clk_hz == 0 || deadtime_ns == 0) {
        return 0;
    }

    /* Період тактового сигналу таймера t_dts у секундах = 1 / timer_clk_hz */
    /* t_dts_ns = 1,000,000,000 / timer_clk_hz */
    double t_dts_ns = 1000000000.0 / (double)timer_clk_hz;
    double dt_ticks = (double)deadtime_ns / t_dts_ns;

    if (dt_ticks <= 127.0) {
        /* Формула 1: DTG[7:0] = DT, при DT <= 127 */
        uint8_t dtg = (uint8_t)dt_ticks;
        return dtg;
    } else if (dt_ticks <= 254.0) {
        /* Формула 2: DT = (64 + DTG[5:0]) * 2, DTG[7:6] = 10 */
        uint8_t val = (uint8_t)((dt_ticks / 2.0) - 64.0);
        if (val > 0x3F) val = 0x3F;
        return (uint8_t)(0x80U | val);
    } else if (dt_ticks <= 504.0) {
        /* Формула 3: DT = (32 + DTG[4:0]) * 8, DTG[7:5] = 110 */
        uint8_t val = (uint8_t)((dt_ticks / 8.0) - 32.0);
        if (val > 0x1F) val = 0x1F;
        return (uint8_t)(0xC0U | val);
    } else {
        /* Формула 4: DT = (32 + DTG[4:0]) * 16, DTG[7:5] = 111 */
        uint8_t val = (uint8_t)((dt_ticks / 16.0) - 32.0);
        if (val > 0x1F) val = 0x1F;
        return (uint8_t)(0xE0U | val);
    }
}

/**
 * @brief Ініціалізація розширеного таймера для комплементарного ШІМ.
 * @param config Вказівник на структуру конфігурації.
 * @return 0 при успіху, від'ємний код помилки при збої.
 */
int pwm_driver_init(const pwm_config_t *config) {
    if (config == NULL || config->timer_clock_hz == 0 || config->pwm_freq_hz == 0) {
        return -1;
    }

    /* 1. Скидання конфігураційних регістрів */
    TIM1->CR1 = 0;
    TIM1->CR2 = 0;
    TIM1->CCER = 0;
    TIM1->BDTR = 0;

    /* 2. Обчислення періоду таймера ARR для режиму вирівнювання по центру (Center-aligned Mode 1)
     * В режимі Center-aligned таймер лічить 0 -> ARR -> 0 (двостороннє лічення),
     * тому f_pwm = f_timer / (2 * PSC * ARR).
     * При PSC = 0 (без дільника) ARR = f_timer / (2 * f_pwm).
     */
    uint32_t arr_val = config->timer_clock_hz / (2U * config->pwm_freq_hz);
    if (arr_val > 0xFFFFU) {
        arr_val = 0xFFFFU; /* Обмеження 16-бітним регістром */
    }
    TIM1->PSC = 0;
    TIM1->ARR = arr_val;

    /* 3. Конфігурація CR1:
     * - CMS = 01 (Center-aligned mode 1: прапорець переповнення ставиться при ліченні вниз)
     * - ARPE = 1 (Auto-reload preload enable — буферизація ARR)
     */
    TIM1->CR1 |= TIM_CR1_CMS_CENTER1 | TIM_CR1_ARPE;

    /* 4. Конфігурація каналів 1, 2, 3 в режим PWM Mode 1 (CCMR1, CCMR2)
     * PWM Mode 1: Канал активний поки CNT < CCRx, далі неактивний.
     * Також вмикаємо Preload enable (OCxPE) для синхронного оновлення коефіцієнтів заповнення.
     */
    TIM1->CCMR1 &= ~((0xFFU << 0) | (0xFFU << 8));
    TIM1->CCMR1 |= (TIM_CCMR_OC1M_PWM1 | TIM_CCMR_OC1PE) |
                   (TIM_CCMR_OC2M_PWM1 | TIM_CCMR_OC2PE);

    TIM1->CCMR2 &= ~(0xFFU << 0);
    TIM1->CCMR2 |= (TIM_CCMR_OC3M_PWM1 | TIM_CCMR_OC3PE);

    /* 5. Увімкнення прямих та комплементарних виходів у регістрі CCER
     * CC1E, CC1NE — фаза A
     * CC2E, CC2NE — фаза B
     * CC3E, CC3NE — фаза C
     */
    TIM1->CCER |= (TIM_CCER_CC1E | TIM_CCER_CC1NE) |
                  (TIM_CCER_CC2E | TIM_CCER_CC2NE) |
                  (TIM_CCER_CC3E | TIM_CCER_CC3NE);

    /* 6. Розрахунок та встановлення мертвого часу (Dead-Time Generator) у BDTR */
    uint8_t dtg = pwm_calculate_dtg(config->timer_clock_hz, config->dead_time_ns);
    TIM1->BDTR = (TIM1->BDTR & ~TIM_BDTR_DTG_MASK) | dtg;

    /* Початкові коефіцієнти заповнення = 50% (нульова напруга на статорі) */
    uint16_t half_arr = (uint16_t)(arr_val / 2U);
    TIM1->CCR1 = half_arr;
    TIM1->CCR2 = half_arr;
    TIM1->CCR3 = half_arr;

    /* 7. Запуск лічильника */
    TIM1->CR1 |= TIM_CR1_CEN;

    return 0;
}

/**
 * @brief Дозвіл або заборона виходів інвертора (Main Output Enable - MOE).
 * @param enable true для ввімкнення ШІМ на вихідних пінах, false для вимкнення (Hi-Z).
 */
void pwm_driver_enable_outputs(bool enable) {
    if (enable) {
        TIM1->BDTR |= TIM_BDTR_MOE;
    } else {
        TIM1->BDTR &= ~TIM_BDTR_MOE;
    }
}

/**
 * @brief Оновлення коефіцієнтів заповнення для 3 фаз (від 0.0 до 1.0).
 * @param duty_a Коефіцієнт заповнення фази A.
 * @param duty_b Коефіцієнт заповнення фази B.
 * @param duty_c Коефіцієнт заповнення фази C.
 */
void pwm_driver_set_duty_cycles(float duty_a, float duty_b, float duty_c) {
    /* Обмеження коефіцієнтів заповнення [0.0, 1.0] */
    if (duty_a < 0.0f) duty_a = 0.0f;
    if (duty_a > 1.0f) duty_a = 1.0f;
    if (duty_b < 0.0f) duty_b = 0.0f;
    if (duty_b > 1.0f) duty_b = 1.0f;
    if (duty_c < 0.0f) duty_c = 0.0f;
    if (duty_c > 1.0f) duty_c = 1.0f;

    uint32_t arr = TIM1->ARR;
    TIM1->CCR1 = (uint16_t)(duty_a * (float)arr);
    TIM1->CCR2 = (uint16_t)(duty_b * (float)arr);
    TIM1->CCR3 = (uint16_t)(duty_c * (float)arr);
}

/**
 * @brief Пряме встановлення регістрів CCR1, CCR2, CCR3 у значеннях відліків.
 */
void pwm_driver_set_raw_ccr(uint16_t ccr_a, uint16_t ccr_b, uint16_t ccr_c) {
    uint32_t arr = TIM1->ARR;
    if (ccr_a > arr) ccr_a = (uint16_t)arr;
    if (ccr_b > arr) ccr_b = (uint16_t)arr;
    if (ccr_c > arr) ccr_c = (uint16_t)arr;

    TIM1->CCR1 = ccr_a;
    TIM1->CCR2 = ccr_b;
    TIM1->CCR3 = ccr_c;
}

/**
 * @brief Отримання значення регістра періоду ARR.
 */
uint16_t pwm_driver_get_period_ticks(void) {
    return (uint16_t)TIM1->ARR;
}

/**
 * @brief Отримання вказівника на структуру регістрів таймера.
 */
TIM_TypeDef *pwm_driver_get_timer_instance(void) {
    return TIM1;
}
