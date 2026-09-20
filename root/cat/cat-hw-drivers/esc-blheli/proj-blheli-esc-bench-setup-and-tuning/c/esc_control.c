#include "esc_control.h"
#include <stdio.h>

/* Імітація регістрів периферійних модулів мікроконтролера */
static struct {
    uint32_t TIM_ARR;   /* Регістр автоперезавантаження таймера (Auto-Reload Register) */
    uint32_t TIM_CCR1;  /* Регістр порівняння таймера каналу 1 (Capture/Compare) */
    uint32_t TIM_PSC;   /* Преддільник частоти таймера (Prescaler) */
    bool TIM_CR1_CEN;   /* Біт ввімкнення таймера (Counter Enable) */
    bool ADC_CR2_ADON;  /* Біт живлення АЦП (ADC Enable) */
} hw_registers;

/**
 * @brief Низькорівневе налаштування апаратного таймера для формування ШІМ 50 Гц.
 */
static void hw_timer_init(void) {
    /* Налаштовуємо таймер на тактову частоту 1 МГц (1 відлік = 1 мкс).
     * Для періоду 20 мс (50 Гц) значення ARR = 20000 - 1. */
    hw_registers.TIM_PSC = 72 - 1;       /* Прикладна тактова 72 МГц / 72 = 1 МГц */
    hw_registers.TIM_ARR = ESC_PWM_PERIOD_US - 1;
    hw_registers.TIM_CCR1 = ESC_PWM_MIN_US; /* Початковий мінімальний імпульс 1000 мкс */
    hw_registers.TIM_CR1_CEN = true;    /* Старт таймера */
}

/**
 * @brief Низькорівневе налаштування аналогово-цифрового перетворювача (АЦП).
 */
static void hw_adc_init(void) {
    /* Увімкнення АЦП для зчитування напруги через резистивний дільник */
    hw_registers.ADC_CR2_ADON = true;
}

/**
 * @brief Оновлення значення апаратного регістра порівняння ШІМ.
 */
static void hw_set_pwm_pulse(uint16_t pulse_us) {
    hw_registers.TIM_CCR1 = pulse_us;
}

void esc_init(esc_driver_t *driver) {
    if (driver == NULL) {
        return;
    }

    driver->current_pulse_us = ESC_PWM_MIN_US;
    driver->bec_voltage = BEC_VOLTAGE_NOMINAL;
    driver->status = BEC_STATUS_OK;
    driver->is_armed = false;
    driver->emergency_stop = false;

    /* Конфігурація периферійних блоків МК */
    hw_timer_init();
    hw_adc_init();

    /* Процедура армування ESC BLHeli:
     * Подача безпечного мінімального імпульсу (1000 мкс) протягом періоду ініціалізації */
    hw_set_pwm_pulse(ESC_PWM_MIN_US);
    driver->is_armed = true;
}

void esc_set_throttle(esc_driver_t *driver, uint16_t pulse_us) {
    if (driver == NULL || !driver->is_armed) {
        return;
    }

    /* Якщо активовано аварійний зупин, примусово скидаємо газ до безпечного мінімуму */
    if (driver->emergency_stop) {
        driver->current_pulse_us = ESC_PWM_MIN_US;
        hw_set_pwm_pulse(ESC_PWM_MIN_US);
        return;
    }

    /* Обмеження діапазону імпульсу стандартними рамками ESC (1000 - 2000 мкс) */
    if (pulse_us < ESC_PWM_MIN_US) {
        pulse_us = ESC_PWM_MIN_US;
    } else if (pulse_us > ESC_PWM_MAX_US) {
        pulse_us = ESC_PWM_MAX_US;
    }

    driver->current_pulse_us = pulse_us;
    hw_set_pwm_pulse(pulse_us);
}

float esc_read_bec_voltage(uint16_t raw_adc) {
    /* Обчислення напруги на вхідному виводі АЦП */
    float v_pin = ((float)raw_adc * BEC_VREF_VOLTS) / BEC_ADC_MAX_VALUE;

    /* Математичний перерахунок вихідної напруги BEC з урахуванням резистивного дільника */
    float v_bec = v_pin * BEC_DIVIDER_RATIO;

    return v_bec;
}

bec_status_t esc_update_bec_status(esc_driver_t *driver, uint16_t raw_adc) {
    if (driver == NULL) {
        return BEC_STATUS_CRITICAL;
    }

    float voltage = esc_read_bec_voltage(raw_adc);
    driver->bec_voltage = voltage;

    if (voltage < BEC_VOLTAGE_CRIT) {
        driver->status = BEC_STATUS_CRITICAL;
        driver->emergency_stop = true; /* Критичний захист: блокуємо роботу ESC */
    } else if (voltage < BEC_VOLTAGE_WARN) {
        driver->status = BEC_STATUS_WARNING;
    } else {
        driver->status = BEC_STATUS_OK;
    }

    return driver->status;
}

void esc_process(esc_driver_t *driver, uint16_t raw_adc, uint16_t requested_throttle_us) {
    if (driver == NULL) {
        return;
    }

    /* 1. Оновлюємо та аналізуємо стан лінії живлення BEC */
    esc_update_bec_status(driver, raw_adc);

    /* 2. Задаємо імпульс дроселювання (з урахуванням захисту від аварії) */
    esc_set_throttle(driver, requested_throttle_us);
}
