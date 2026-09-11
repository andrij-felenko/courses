/**
 * @file laser_driver.c
 * @brief Реалізація драйвера периферії мікроконтролера для керування лазерним модулем.
 *
 * Налаштування One-Pulse Mode таймера, обробка переривання EXTI, медіанна фільтрація
 * сигналів оптичного зворотного зв'язку й температурного датчика, кінцевий автомат безпеки.
 */

#include "laser_driver.h"
#include <string.h>

/* --- Бітові маски регістрів таймера (архітектура ARM Cortex-M / STM32) --- */
#define TIM_CR1_CEN             (1U << 0)  /**< Counter Enable */
#define TIM_CR1_OPM             (1U << 3)  /**< One-Pulse Mode */
#define TIM_CR1_ARPE            (1U << 7)  /**< Auto-reload preload enable */

#define TIM_CCMR1_OC1M_PWM1     (6U << 4)  /**< OC1M = 0110 (PWM mode 1) */
#define TIM_CCMR1_OC1PE         (1U << 3)  /**< Output Compare 1 preload enable */

#define TIM_CCER_CC1E           (1U << 0)  /**< Capture/Compare 1 output enable */
#define TIM_CCER_CC1P           (1U << 1)  /**< Capture/Compare 1 polarity (1 = active low) */

#define TIM_SMCR_SMS_TRIGGER    (6U << 0)  /**< Slave Mode: Trigger Mode (start on trigger) */
#define TIM_SMCR_TS_TI1FP1      (5U << 4)  /**< Trigger Selection: TI1FP1 (вхід з EXTI/камери) */

#define TIM_EGR_UG              (1U << 0)  /**< Update Generation (тіньове перезавантаження) */

/**
 * @brief Медіанний фільтр 5-го порядку методом сортування вставками.
 * Відсікає поодинокі імпульсні завади комутації та наведення без затримки фази.
 */
static uint16_t median_filter_5(const uint16_t *buffer) {
    uint16_t s[LASER_MEDIAN_WINDOW_SIZE];
    for (int i = 0; i < LASER_MEDIAN_WINDOW_SIZE; ++i) {
        s[i] = buffer[i];
    }
    for (int i = 1; i < LASER_MEDIAN_WINDOW_SIZE; ++i) {
        uint16_t key = s[i];
        int j = i - 1;
        while (j >= 0 && s[j] > key) {
            s[j + 1] = s[j];
            j--;
        }
        s[j + 1] = key;
    }
    return s[LASER_MEDIAN_WINDOW_SIZE / 2];
}

/**
 * @brief Перерахунок напруги термістора у градуси Цельсія (лінеаризована модель NTC).
 */
static float convert_ntc_mv_to_celsius(uint16_t mv) {
    /* Модель лінійного наближення чутливості 10 мВ / град. C із базою 25 C на 1000 мВ */
    float temp = 25.0f + ((float)mv - 1000.0f) * 0.1f;
    return temp;
}

bool laser_driver_init(laser_device_t *dev, laser_hw_timer_t *timer_regs, const laser_config_t *cfg) {
    if (dev == NULL || timer_regs == NULL || cfg == NULL) {
        return false;
    }

    dev->timer = timer_regs;
    dev->config = *cfg;
    dev->state = LASER_STATE_DISABLED;
    dev->fault_code = LASER_FAULT_NONE;
    dev->current_mode = LASER_MODE_STROBE_OPM;
    dev->filter_index = 0;
    dev->emission_start_tick_ms = 0;

    memset(&dev->telemetry, 0, sizeof(dev->telemetry));
    dev->telemetry.interlock_closed = false;

    /* Заповнюємо початкові буфери фільтра безпечними нулями */
    for (int i = 0; i < LASER_MEDIAN_WINDOW_SIZE; ++i) {
        dev->pd_history[i] = 0;
        dev->temp_history[i] = 1000; /* ~25 C */
    }

    /* Апаратна ініціалізація таймера: вимикаємо лічильник та генерацію */
    dev->timer->CR1 = 0;
    dev->timer->CCER &= ~TIM_CCER_CC1E;
    dev->timer->CNT = 0;

    /* Початкова конфігурація під режим стробування */
    laser_driver_configure_one_pulse(dev, dev->config.default_strobe_us);

    return true;
}

void laser_driver_configure_one_pulse(laser_device_t *dev, uint32_t duration_us) {
    if (dev == NULL || dev->timer == NULL || duration_us == 0) {
        return;
    }

    /* Безпечне відключення виходу перед перебудовою конфігурації */
    dev->timer->CR1 &= ~TIM_CR1_CEN;
    dev->timer->CCER &= ~TIM_CCER_CC1E;

    /* 1. Налаштовуємо переддільник для мікросекундної шкали (1 МГц = 1 мкс/тік) */
    uint32_t psc_val = (dev->config.timer_clock_hz / 1000000U) - 1U;
    dev->timer->PSC = psc_val;

    /* 2. Задаємо тривалість активного імпульсу та період оновлення
     * У режимі One-Pulse Mode ARR визначає момент автоматичної зупинки таймера.
     */
    dev->timer->ARR = duration_us + 2U; /* Невеликий захисний інтервал затухання */
    dev->timer->CCR1 = duration_us;      /* Активна тривалість відкритого стану FET */

    /* 3. Режим ШІМ-1 на каналі 1 з буферизацією (preload) */
    dev->timer->CCMR1 = TIM_CCMR1_OC1M_PWM1 | TIM_CCMR1_OC1PE;

    /* 4. Slave Mode Trigger: апаратний запуск по фронту сигналу камери (TI1FP1) */
    dev->timer->SMCR = TIM_SMCR_SMS_TRIGGER | TIM_SMCR_TS_TI1FP1;

    /* 5. One-Pulse Mode: біт OPM зупиняє лічильник (CEN=0) одразу по досягненню ARR */
    dev->timer->CR1 = TIM_CR1_OPM | TIM_CR1_ARPE;

    /* Оновлюємо тіньові регістри */
    dev->timer->EGR = TIM_EGR_UG;
    dev->timer->SR = 0; /* Скидаємо прапорець оновлення */

    /* Дозволяємо вихід на драйвер діода */
    dev->timer->CCER |= TIM_CCER_CC1E;
    dev->current_mode = LASER_MODE_STROBE_OPM;
}

void laser_driver_configure_pwm(laser_device_t *dev, uint32_t frequency_hz, uint16_t duty_permille) {
    if (dev == NULL || dev->timer == NULL || frequency_hz == 0 || duty_permille > 1000) {
        return;
    }

    dev->timer->CR1 &= ~TIM_CR1_CEN;
    dev->timer->CCER &= ~TIM_CCER_CC1E;

    /* Розрахунок періоду таймера для заданої частоти ШІМ */
    uint32_t timer_clk = dev->config.timer_clock_hz;
    uint32_t period_ticks = timer_clk / frequency_hz;

    /* Якщо період перевищує 16-бітний таймер, підбираємо дільник PSC */
    uint32_t psc = 0;
    while (period_ticks > 65535U) {
        psc++;
        period_ticks = timer_clk / (frequency_hz * (psc + 1U));
    }

    dev->timer->PSC = psc;
    dev->timer->ARR = period_ticks - 1U;

    /* Коефіцієнт заповнення у відліках таймера */
    uint32_t ccr_val = (period_ticks * duty_permille) / 1000U;
    dev->timer->CCR1 = ccr_val;

    /* Безперервний ШІМ без OPM і без Slave Trigger */
    dev->timer->SMCR = 0;
    dev->timer->CCMR1 = TIM_CCMR1_OC1M_PWM1 | TIM_CCMR1_OC1PE;
    dev->timer->CR1 = TIM_CR1_ARPE;

    dev->timer->EGR = TIM_EGR_UG;
    dev->timer->SR = 0;

    dev->timer->CCER |= TIM_CCER_CC1E;
    dev->timer->CR1 |= TIM_CR1_CEN; /* Запуск безперервної генерації */
    dev->current_mode = LASER_MODE_CONTINUOUS_PWM;
}

void laser_driver_on_exti_trigger_isr(laser_device_t *dev) {
    if (dev == NULL) {
        return;
    }

    /* Перевірка стану готовності: якщо безпека порушена, ігноруємо зовнішній тригер */
    if (dev->state != LASER_STATE_READY && dev->state != LASER_STATE_STROBING) {
        return;
    }

    dev->state = LASER_STATE_STROBING;
    dev->telemetry.pulse_count++;

    /* В апаратному режимі OPM запуск здійснюється самим входом TI1FP1 апаратно.
     * Якщо використовується програмна ретрансляція EXTI -> Timer:
     */
    dev->timer->CR1 |= TIM_CR1_CEN;
}

void laser_driver_update_adc_samples(laser_device_t *dev, uint16_t raw_photodiode, uint16_t raw_temp_mv) {
    if (dev == NULL) {
        return;
    }

    /* Запис у циклічний буфер вікна фільтра */
    dev->pd_history[dev->filter_index] = raw_photodiode;
    dev->temp_history[dev->filter_index] = raw_temp_mv;

    dev->filter_index = (dev->filter_index + 1U) % LASER_MEDIAN_WINDOW_SIZE;

    /* Застосування медіанної фільтрації */
    dev->telemetry.filtered_photodiode_raw = median_filter_5(dev->pd_history);
    uint16_t med_temp_mv = median_filter_5(dev->temp_history);
    dev->telemetry.filtered_temperature_c = convert_ntc_mv_to_celsius(med_temp_mv);
}

void laser_driver_set_interlock(laser_device_t *dev, bool is_closed) {
    if (dev == NULL) {
        return;
    }
    dev->telemetry.interlock_closed = is_closed;
}

void laser_driver_emergency_shutdown(laser_device_t *dev, laser_fault_t fault) {
    if (dev == NULL) {
        return;
    }

    /* Миттєве апаратне вимкнення виходу таймера */
    if (dev->timer != NULL) {
        dev->timer->CR1 &= ~TIM_CR1_CEN;
        dev->timer->CCER &= ~TIM_CCER_CC1E;
        dev->timer->CCR1 = 0;
    }

    dev->state = LASER_STATE_FAULT;
    dev->fault_code = fault;
}

void laser_driver_process_fsm(laser_device_t *dev, uint32_t current_tick_ms) {
    if (dev == NULL) {
        return;
    }

    /* 1. Блискавичний захист за критичними умовами (діє в будь-якому стані) */
    if (!dev->telemetry.interlock_closed) {
        if (dev->state != LASER_STATE_FAULT && dev->state != LASER_STATE_DISABLED) {
            laser_driver_emergency_shutdown(dev, LASER_FAULT_INTERLOCK_OPEN);
            return;
        }
    }

    if (dev->telemetry.filtered_temperature_c > dev->config.max_temp_celsius) {
        laser_driver_emergency_shutdown(dev, LASER_FAULT_OVERTEMP);
        return;
    }

    /* Захист від COD: якщо фотодіод детектує небезпечний стрибок оптичної густини */
    if (dev->telemetry.filtered_photodiode_raw > dev->config.max_photodiode_raw) {
        laser_driver_emergency_shutdown(dev, LASER_FAULT_OVERPOWER_COD);
        return;
    }

    /* 2. Обробка переходів скінченного автомата (FSM) */
    switch (dev->state) {
        case LASER_STATE_DISABLED:
            if (dev->telemetry.interlock_closed && dev->fault_code == LASER_FAULT_NONE) {
                dev->state = LASER_STATE_READY;
            }
            break;

        case LASER_STATE_READY:
            /* Готовий до роботи, очікує строб EXTI або команду увімкнення ШІМ */
            break;

        case LASER_STATE_STROBING:
            /* У режимі стробування таймер OPM вимикається апаратно після імпульсу.
             * Перевіряємо біт CEN: коли він скидається апаратно в 0 — повертаємося в READY.
             */
            if ((dev->timer->CR1 & TIM_CR1_CEN) == 0U) {
                dev->state = LASER_STATE_READY;
            } else {
                /* Перевірка сторожового таймера максимальної тривалості спалаху */
                if (dev->emission_start_tick_ms == 0) {
                    dev->emission_start_tick_ms = current_tick_ms;
                } else if ((current_tick_ms - dev->emission_start_tick_ms) > dev->config.watchdog_timeout_ms) {
                    laser_driver_emergency_shutdown(dev, LASER_FAULT_WATCHDOG_TIMEOUT);
                }
            }
            break;

        case LASER_STATE_CONTINUOUS:
            /* У неперервному режимі контролюємо робочий інтервал */
            if (dev->emission_start_tick_ms != 0 &&
                (current_tick_ms - dev->emission_start_tick_ms) > (dev->config.watchdog_timeout_ms * 10U)) {
                /* Запобігання перегріву від нескінченного неперервного світіння */
                laser_driver_emergency_shutdown(dev, LASER_FAULT_WATCHDOG_TIMEOUT);
            }
            break;

        case LASER_STATE_FAULT:
            /* Перебуваємо в аварійному стані до виклику laser_driver_reset_fault */
            dev->timer->CR1 &= ~TIM_CR1_CEN;
            dev->timer->CCER &= ~TIM_CCER_CC1E;
            break;

        default:
            laser_driver_emergency_shutdown(dev, LASER_FAULT_ADC_UNSTABLE);
            break;
    }
}

bool laser_driver_reset_fault(laser_device_t *dev) {
    if (dev == NULL) {
        return false;
    }

    /* Заборонено скидати помилку, якщо аварійні фактори ще присутні */
    if (!dev->telemetry.interlock_closed) {
        return false;
    }
    if (dev->telemetry.filtered_temperature_c > dev->config.max_temp_celsius) {
        return false;
    }
    if (dev->telemetry.filtered_photodiode_raw > dev->config.max_photodiode_raw) {
        return false;
    }

    dev->fault_code = LASER_FAULT_NONE;
    dev->state = LASER_STATE_READY;
    dev->emission_start_tick_ms = 0;

    /* Відновлення виходу таймера у готовність */
    dev->timer->CCER |= TIM_CCER_CC1E;
    return true;
}

laser_state_t laser_driver_get_state(const laser_device_t *dev) {
    return dev ? dev->state : LASER_STATE_FAULT;
}

void laser_driver_get_telemetry(const laser_device_t *dev, laser_telemetry_t *out_telemetry) {
    if (dev != NULL && out_telemetry != NULL) {
        *out_telemetry = dev->telemetry;
    }
}
