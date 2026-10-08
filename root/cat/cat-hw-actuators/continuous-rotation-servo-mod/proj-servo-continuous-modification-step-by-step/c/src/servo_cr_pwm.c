#include "servo_cr_pwm.h"
#include <stddef.h>

/* Внутрішній стан модуля */
static TIM_TypeDef *s_timer = NULL;
static bool s_invert_direction = false;
static uint16_t s_current_pulse_us = SERVO_CR_PULSE_NEUTRAL_US;
static bool s_initialized = false;

int servo_cr_pwm_init(const servo_cr_pwm_config_t *config)
{
    if (config == NULL || config->timer_instance == NULL || config->timer_clock_hz == 0U) {
        return -1;
    }

    uint16_t start_pulse = config->initial_pulse_us;
    if (start_pulse < SERVO_CR_PULSE_MIN_US || start_pulse > SERVO_CR_PULSE_MAX_US) {
        start_pulse = SERVO_CR_PULSE_NEUTRAL_US;
    }

    s_timer = config->timer_instance;
    s_invert_direction = config->invert_direction;

    /*
     * Обчислення дільника частоти (Prescaler) для забезпечення тактування 1 МГц (1 мкс на тік).
     * PSC = (F_timer / 1_000_000 Гц) - 1
     */
    uint32_t prescaler_val = (config->timer_clock_hz / 1000000U);
    if (prescaler_val > 0U) {
        prescaler_val -= 1U;
    }
    if (prescaler_val > 0xFFFFU) {
        return -1; /* Prescaler переповнює 16-бітне значення */
    }

    /* 1. Зупинка таймера перед переконфігурацією */
    s_timer->CR1 &= ~TIM_CR1_CEN;

    /* 2. Налаштування дільника PSC та лічильника автоперезавантаження ARR (20 000 мкс = 20 мс = 50 Гц) */
    s_timer->PSC = (uint16_t)prescaler_val;
    s_timer->ARR = (uint32_t)(SERVO_CR_PERIOD_US - 1U);

    /* 3. Конфігурація каналу 1 у режим ШІМ 1 (PWM Mode 1) та вмикання буферизації (Preload) */
    uint32_t ccmr1 = s_timer->CCMR1;
    ccmr1 &= ~(0x70U | (1U << 3)); /* Очищення полів OC1M та OC1PE */
    ccmr1 |= (TIM_CCMR1_OC1M_PWM1 | TIM_CCMR1_OC1PE);
    s_timer->CCMR1 = ccmr1;

    /* 4. Встановлення початкового значення тривалості імпульсу в CCR1 */
    s_timer->CCR1 = (uint32_t)start_pulse;
    s_current_pulse_us = start_pulse;

    /* 5. Дозвіл виходу каналу 1 (CC1E) та активний високий рівень */
    s_timer->CCER &= ~(TIM_CCER_CC1P);
    s_timer->CCER |= TIM_CCER_CC1E;

    /* 6. Увімкнення буферизації регістра ARR в CR1 */
    s_timer->CR1 |= TIM_CR1_ARPE;

    /* 7. Для покращених таймерів — увімкнення головного виходу (MOE) */
    s_timer->BDTR |= TIM_BDTR_MOE;

    /* 8. Генерація події оновлення (Update Generation) для застосування PSC та ARR */
    s_timer->EGR |= TIM_EGR_UG;

    /* 9. Запуск апаратного лічильника */
    s_timer->CR1 |= TIM_CR1_CEN;

    s_initialized = true;
    return 0;
}

int servo_cr_pwm_set_pulse_us(uint16_t pulse_us)
{
    if (!s_initialized || s_timer == NULL) {
        return -1;
    }

    /* Обмеження тривалості імпульсу у безпечних фізичних межах 1000..2000 мкс */
    if (pulse_us < SERVO_CR_PULSE_MIN_US) {
        pulse_us = SERVO_CR_PULSE_MIN_US;
    } else if (pulse_us > SERVO_CR_PULSE_MAX_US) {
        pulse_us = SERVO_CR_PULSE_MAX_US;
    }

    /* Прямий запис у регістр CCR1 для зміни тривалості імпульсу без блокування CPU */
    s_timer->CCR1 = (uint32_t)pulse_us;
    s_current_pulse_us = pulse_us;

    return 0;
}

int servo_cr_pwm_set_speed(float speed_pct)
{
    if (!s_initialized) {
        return -1;
    }

    /* Обмеження відсотків у межах [-100.0, +100.0] */
    if (speed_pct < SERVO_CR_SPEED_MIN_PCT) {
        speed_pct = SERVO_CR_SPEED_MIN_PCT;
    } else if (speed_pct > SERVO_CR_SPEED_MAX_PCT) {
        speed_pct = SERVO_CR_SPEED_MAX_PCT;
    }

    if (s_invert_direction) {
        speed_pct = -speed_pct;
    }

    /*
     * Лінійна інтерполяція відсотка швидкості у тривалість ШІМ-імпульсу:
     * -100.0% -> 1000 мкс
     *    0.0% -> 1500 мкс
     * +100.0% -> 2000 мкс
     */
    float pulse_f = (float)SERVO_CR_PULSE_NEUTRAL_US + (speed_pct / 100.0f) * 500.0f;
    uint16_t pulse_us = (uint16_t)(pulse_f + 0.5f);

    return servo_cr_pwm_set_pulse_us(pulse_us);
}

uint16_t servo_cr_pwm_get_pulse_us(void)
{
    if (!s_initialized || s_timer == NULL) {
        return SERVO_CR_PULSE_NEUTRAL_US;
    }
    return (uint16_t)s_timer->CCR1;
}

float servo_cr_pwm_get_speed(void)
{
    if (!s_initialized) {
        return 0.0f;
    }

    uint16_t pulse = servo_cr_pwm_get_pulse_us();
    float speed_pct = ((float)pulse - (float)SERVO_CR_PULSE_NEUTRAL_US) / 500.0f * 100.0f;

    if (s_invert_direction) {
        speed_pct = -speed_pct;
    }

    return speed_pct;
}

void servo_cr_pwm_stop(void)
{
    (void)servo_cr_pwm_set_pulse_us(SERVO_CR_PULSE_NEUTRAL_US);
}
