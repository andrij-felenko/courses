#include "pwm_driver.h"
#include <stddef.h>

int pwm_driver_init(pwm_driver_t *driver, TIM_TypeDef *timer, uint32_t channel, uint32_t clock_hz)
{
    if (driver == NULL || timer == NULL) {
        return -1;
    }
    if (channel < 1U || channel > 4U) {
        return -1;
    }
    if (clock_hz < 1000000U) {
        return -1;
    }

    driver->timer = timer;
    driver->channel = channel;
    driver->timer_clock_hz = clock_hz;
    driver->current_pulse_us = PWM_PULSE_NEUTRAL_US;
    driver->is_enabled = false;

    /* Обчислення дільника частоти PSC для отримання кванту таймера в 1 мкс (1 МГц) */
    uint32_t prescaler = (clock_hz / 1000000U) - 1U;
    driver->timer->PSC = prescaler;

    /* Налаштування періоду 20 мс (20000 мкс) у регістрі автоперезавантаження ARR */
    driver->timer->ARR = PWM_PERIOD_US - 1U;

    /* Конфігурація режиму ШІМ (PWM Mode 1) та дозволу попереднього завантаження */
    if (channel == 1U) {
        driver->timer->CCMR1 &= ~(0xFFU);
        driver->timer->CCMR1 |= (TIM_CCMR1_OC1M_PWM1 | TIM_CCMR1_OC1PE);
        driver->timer->CCR1 = driver->current_pulse_us;
    } else if (channel == 2U) {
        driver->timer->CCMR1 &= ~(0xFF00U);
        driver->timer->CCMR1 |= ((TIM_CCMR1_OC1M_PWM1 | TIM_CCMR1_OC1PE) << 8);
        driver->timer->CCR2 = driver->current_pulse_us;
    } else if (channel == 3U) {
        driver->timer->CCMR2 &= ~(0xFFU);
        driver->timer->CCMR2 |= (TIM_CCMR1_OC1M_PWM1 | TIM_CCMR1_OC1PE);
        driver->timer->CCR3 = driver->current_pulse_us;
    } else if (channel == 4U) {
        driver->timer->CCMR2 &= ~(0xFF00U);
        driver->timer->CCMR2 |= ((TIM_CCMR1_OC1M_PWM1 | TIM_CCMR1_OC1PE) << 8);
        driver->timer->CCR4 = driver->current_pulse_us;
    }

    /* Увімкнення буферизації ARR та генерація оновлення регістрів */
    driver->timer->CR1 |= TIM_CR1_ARPE;
    driver->timer->EGR |= TIM_EGR_UG;

    /* Увімкнення таймера */
    driver->timer->CR1 |= TIM_CR1_CEN;

    /* Активація виходу каналу */
    return pwm_driver_attach(driver);
}

int pwm_driver_set_pulse_us(pwm_driver_t *driver, uint16_t pulse_us)
{
    if (driver == NULL || driver->timer == NULL) {
        return -1;
    }

    /* Обмеження тривалості імпульсу в безпечному апаратному діапазоні */
    if (pulse_us < PWM_PULSE_MIN_US) {
        pulse_us = PWM_PULSE_MIN_US;
    } else if (pulse_us > PWM_PULSE_MAX_US) {
        pulse_us = PWM_PULSE_MAX_US;
    }

    driver->current_pulse_us = pulse_us;

    /* Якщо вихід активний, відразу оновлюємо значення порівняння */
    if (driver->is_enabled) {
        switch (driver->channel) {
            case 1U: driver->timer->CCR1 = pulse_us; break;
            case 2U: driver->timer->CCR2 = pulse_us; break;
            case 3U: driver->timer->CCR3 = pulse_us; break;
            case 4U: driver->timer->CCR4 = pulse_us; break;
            default: return -1;
        }
    }

    return 0;
}

int pwm_driver_detach(pwm_driver_t *driver)
{
    if (driver == NULL || driver->timer == NULL) {
        return -1;
    }

    /* Апаратне вимкнення виходу відповідного каналу таймера */
    switch (driver->channel) {
        case 1U:
            driver->timer->CCER &= ~TIM_CCER_CC1E;
            driver->timer->CCR1 = 0U;
            break;
        case 2U:
            driver->timer->CCER &= ~TIM_CCER_CC2E;
            driver->timer->CCR2 = 0U;
            break;
        case 3U:
            driver->timer->CCER &= ~TIM_CCER_CC3E;
            driver->timer->CCR3 = 0U;
            break;
        case 4U:
            driver->timer->CCER &= ~TIM_CCER_CC4E;
            driver->timer->CCR4 = 0U;
            break;
        default:
            return -1;
    }

    driver->is_enabled = false;
    return 0;
}

int pwm_driver_attach(pwm_driver_t *driver)
{
    if (driver == NULL || driver->timer == NULL) {
        return -1;
    }

    /* Встановлення ширини імпульсу та повторна активація каналу */
    pwm_driver_set_pulse_us(driver, driver->current_pulse_us);

    switch (driver->channel) {
        case 1U: driver->timer->CCER |= TIM_CCER_CC1E; break;
        case 2U: driver->timer->CCER |= TIM_CCER_CC2E; break;
        case 3U: driver->timer->CCER |= TIM_CCER_CC3E; break;
        case 4U: driver->timer->CCER |= TIM_CCER_CC4E; break;
        default: return -1;
    }

    driver->is_enabled = true;
    return 0;
}

bool pwm_driver_is_enabled(const pwm_driver_t *driver)
{
    if (driver == NULL) {
        return false;
    }
    return driver->is_enabled;
}

uint16_t pwm_driver_get_pulse_us(const pwm_driver_t *driver)
{
    if (driver == NULL) {
        return 0U;
    }
    return driver->current_pulse_us;
}
