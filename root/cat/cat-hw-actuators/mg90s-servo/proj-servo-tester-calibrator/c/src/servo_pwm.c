#include "servo_pwm.h"
#include <stddef.h>

/**
 * @file servo_pwm.c
 * @brief Реалізація драйвера точного ШІМ-керування сервоприводом MG90S V2.
 *
 * Забезпечує конфігурування дільника частоти (PSC) та регістра автоперезавантаження (ARR),
 * а також атомарне оновлення регістру порівняння (CCR1) для усунення тремтіння (джитера) вала.
 */

/* Приватний екземпляр регістрів таймера (симуляція апаратного периферійного модуля) */
static TIM_TypeDef g_servo_timer_hw;
static bool g_servo_pwm_initialized = false;
static uint16_t g_current_pulse_us = SERVO_PULSE_CENTER_US;

int servo_pwm_init(const servo_pwm_config_t *config)
{
    if (config == NULL || config->timer_clock_hz < 1000000U) {
        return -1;
    }

    /* 1. Обчислення дільника Prescaler (PSC) для отримання точності 1 мікросекунда на такт.
     * Частота таймера після дільника = 1 МГц (період 1 мкс).
     * PSC = (f_timer / 1_000_000) - 1
     */
    uint32_t prescaler_val = (config->timer_clock_hz / 1000000U) - 1U;
    g_servo_timer_hw.PSC = prescaler_val;

    /* 2. Обчислення регістра Auto-Reload (ARR) для періоду 20 мкс (50 Гц).
     * Оскільки 1 такт = 1 мкс, для 20000 мкс потрібно (20000 - 1) тиків.
     */
    g_servo_timer_hw.ARR = SERVO_PERIOD_US - 1U;

    /* 3. Налаштування режиму порівняння CCMR1:
     * - PWM Mode 1: сигнал активний, поки CNT < CCR1, потім неактивний.
     * - OC1PE (Preload Enable): зміни в CCR1 записуються в буфер і наберуть чинності тільки при події оновлення (Update Event).
     *   Це запобігає появі хибних коротких імпульсів та тремтінню вала.
     */
    g_servo_timer_hw.CCMR1 = TIM_CCMR1_OC1M_PWM1 | TIM_CCMR1_OC1PE;

    /* 4. Ввімкнення теневого регістру ARR (ARPE) */
    g_servo_timer_hw.CR1 |= TIM_CR1_ARPE;

    /* 5. Встановлення початкового значення тривалості імпульсу */
    uint16_t init_pulse = config->initial_pulse_us;
    if (init_pulse < SERVO_PULSE_MIN_US) {
        init_pulse = SERVO_PULSE_MIN_US;
    } else if (init_pulse > SERVO_PULSE_MAX_US) {
        init_pulse = SERVO_PULSE_MAX_US;
    }
    g_servo_timer_hw.CCR1 = init_pulse;
    g_current_pulse_us = init_pulse;

    /* 6. Конфігурація полярності та дозволу виходу CCER */
    uint32_t ccer_val = TIM_CCER_CC1E;
    if (config->invert_polarity) {
        ccer_val |= TIM_CCER_CC1P;
    }
    g_servo_timer_hw.CCER = ccer_val;

    /* 7. Атомарне генерування події оновлення (UG) для примусового перезавантаження дільників */
    g_servo_timer_hw.EGR |= TIM_EGR_UG;

    /* 8. Запуск лічильника таймера */
    g_servo_timer_hw.CR1 |= TIM_CR1_CEN;

    g_servo_pwm_initialized = true;
    return 0;
}

int servo_pwm_set_pulse_us(uint16_t pulse_us)
{
    if (!g_servo_pwm_initialized) {
        return -1;
    }

    /* Обмеження безпечних меж імпульсу для сервоприводу MG90S V2 */
    if (pulse_us < SERVO_PULSE_MIN_US) {
        pulse_us = SERVO_PULSE_MIN_US;
    } else if (pulse_us > SERVO_PULSE_MAX_US) {
        pulse_us = SERVO_PULSE_MAX_US;
    }

    /* Запис у буферизований регістр CCR1.
     * Оновлення відбудеться синхронно із завершенням поточного періоду 20 мкс.
     */
    g_servo_timer_hw.CCR1 = pulse_us;
    g_current_pulse_us = pulse_us;

    return 0;
}

int servo_pwm_set_angle(float angle_deg)
{
    if (!g_servo_pwm_initialized) {
        return -1;
    }

    /* Валідація та обмеження кута */
    if (angle_deg < SERVO_ANGLE_MIN_DEG) {
        angle_deg = SERVO_ANGLE_MIN_DEG;
    } else if (angle_deg > SERVO_ANGLE_MAX_DEG) {
        angle_deg = SERVO_ANGLE_MAX_DEG;
    }

    /* Лінійне масштабування кута [0..180] у ширину імпульсу [1000..2000] мкс */
    float pulse_float = (float)SERVO_PULSE_MIN_US +
                        (angle_deg / SERVO_ANGLE_MAX_DEG) * (float)(SERVO_PULSE_MAX_US - SERVO_PULSE_MIN_US);

    uint16_t pulse_us = (uint16_t)(pulse_float + 0.5f);
    return servo_pwm_set_pulse_us(pulse_us);
}

uint16_t servo_pwm_get_current_pulse_us(void)
{
    return g_current_pulse_us;
}

float servo_pwm_get_current_angle(void)
{
    if (g_current_pulse_us <= SERVO_PULSE_MIN_US) {
        return SERVO_ANGLE_MIN_DEG;
    }
    if (g_current_pulse_us >= SERVO_PULSE_MAX_US) {
        return SERVO_ANGLE_MAX_DEG;
    }

    float angle = ((float)(g_current_pulse_us - SERVO_PULSE_MIN_US) /
                  (float)(SERVO_PULSE_MAX_US - SERVO_PULSE_MIN_US)) * SERVO_ANGLE_MAX_DEG;
    return angle;
}

void servo_pwm_enable(bool enable)
{
    if (enable) {
        g_servo_timer_hw.CCER |= TIM_CCER_CC1E;
        g_servo_timer_hw.CR1 |= TIM_CR1_CEN;
    } else {
        g_servo_timer_hw.CCER &= ~TIM_CCER_CC1E;
        g_servo_timer_hw.CR1 &= ~TIM_CR1_CEN;
    }
}

TIM_TypeDef *servo_pwm_get_timer_instance(void)
{
    return &g_servo_timer_hw;
}
