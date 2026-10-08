#include "liquid_level.h"
#include "mcu_adc_gpio.h"

/**
 * @brief Допоміжна функція обмеження значення в заданих межах.
 */
static float clampf(float val, float min_val, float max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

/**
 * @brief Оновлення буфера та обчислення пікового значення АЦП.
 *
 * Алгоритм знаходить максимальне значення (гребінь хвилі) у ковзному вікні,
 * що дозволяє придушити просідання сигналу при сплесках та коливаннях поверхні рідини.
 */
static uint16_t process_peak_filter(liquid_level_t *dev, uint16_t raw_adc) {
    dev->adc_window[dev->window_head] = raw_adc;
    dev->window_head = (dev->window_head + 1) % dev->config.peak_window_size;

    if (dev->window_count < dev->config.peak_window_size) {
        dev->window_count++;
    }

    uint16_t peak_val = dev->adc_window[0];
    for (uint8_t i = 1; i < dev->window_count; i++) {
        if (dev->adc_window[i] > peak_val) {
            peak_val = dev->adc_window[i];
        }
    }
    return peak_val;
}

/**
 * @brief Програмний антибрязкот для тумблерного/поплавкового GPIO.
 */
static void debounce_gpio(bool raw_pin_state, bool *debounced_state, bool *raw_state_store,
                          uint32_t *last_change_ms, uint32_t debounce_ms, uint32_t current_time_ms) {
    if (raw_pin_state != *raw_state_store) {
        *raw_state_store = raw_pin_state;
        *last_change_ms = current_time_ms;
    } else {
        if ((current_time_ms - *last_change_ms) >= debounce_ms) {
            *debounced_state = raw_pin_state;
        }
    }
}

/**
 * @brief Перетворення цифрового відліку АЦП у відсотки рівня (0..100%).
 */
static float adc_to_percentage(uint16_t adc_val, uint16_t min_raw, uint16_t max_raw) {
    if (min_raw >= max_raw) {
        return 0.0f;
    }
    if (adc_val <= min_raw) {
        return 0.0f;
    }
    if (adc_val >= max_raw) {
        return 100.0f;
    }
    float pct = ((float)(adc_val - min_raw) / (float)(max_raw - min_raw)) * 100.0f;
    return clampf(pct, 0.0f, 100.0f);
}

liquid_level_status_t liquid_level_init(liquid_level_t *dev, const liquid_level_config_t *config) {
    if (dev == NULL || config == NULL) {
        return LIQUID_LEVEL_ERROR_NULL_PTR;
    }

    if (config->adc_min_raw >= config->adc_max_raw ||
        config->peak_window_size == 0 ||
        config->peak_window_size > LIQUID_LEVEL_PEAK_WINDOW_MAX ||
        config->threshold_turn_on_pct < 0.0f || config->threshold_turn_on_pct > 100.0f ||
        config->threshold_turn_off_pct < 0.0f || config->threshold_turn_off_pct > 100.0f) {
        return LIQUID_LEVEL_ERROR_PARAM;
    }

    dev->config = *config;
    dev->window_head = 0;
    dev->window_count = 0;
    for (uint8_t i = 0; i < LIQUID_LEVEL_PEAK_WINDOW_MAX; i++) {
        dev->adc_window[i] = config->adc_min_raw;
    }

    dev->raw_low_state = false;
    dev->debounced_low_state = false;
    dev->low_state_change_ms = 0;

    dev->raw_high_state = false;
    dev->debounced_high_state = false;
    dev->high_state_change_ms = 0;

    dev->pump_state = PUMP_STATE_OFF;
    dev->pump_start_time_ms = 0;
    dev->initial_pump_level_pct = 0.0f;
    dev->last_process_time_ms = 0;

    dev->data.raw_adc = config->adc_min_raw;
    dev->data.peak_adc = config->adc_min_raw;
    dev->data.level_pct = 0.0f;
    dev->data.low_float_active = false;
    dev->data.high_float_active = false;
    dev->data.pump_state = PUMP_STATE_OFF;
    dev->data.pump_running_time_ms = 0;
    dev->data.last_fault_time_ms = 0;

    /* Ініціалізація периферії HAL */
    if (!mcu_adc_init()) {
        return LIQUID_LEVEL_ERROR_HAL;
    }
    if (!mcu_gpio_init(config->gpio_pin_low_float, MCU_GPIO_DIR_INPUT) ||
        !mcu_gpio_init(config->gpio_pin_high_float, MCU_GPIO_DIR_INPUT) ||
        !mcu_gpio_init(config->gpio_pin_pump_relay, MCU_GPIO_DIR_OUTPUT)) {
        return LIQUID_LEVEL_ERROR_HAL;
    }

    /* Безпечне початкове вимкнення реле помпи */
    mcu_gpio_write(config->gpio_pin_pump_relay, false);

    dev->initialized = true;
    return LIQUID_LEVEL_OK;
}

liquid_level_status_t liquid_level_process(liquid_level_t *dev, uint32_t current_time_ms) {
    if (dev == NULL) {
        return LIQUID_LEVEL_ERROR_NULL_PTR;
    }
    if (!dev->initialized) {
        return LIQUID_LEVEL_ERROR_PARAM;
    }

    dev->last_process_time_ms = current_time_ms;

    /* 1. Зчитування аналогового каналу АЦП */
    uint16_t raw_adc = 0;
    if (!mcu_adc_read_raw(dev->config.adc_channel, &raw_adc)) {
        return LIQUID_LEVEL_ERROR_HAL;
    }

    /* 2. Цифровізація пікових значень та конвертація у відсотки */
    uint16_t peak_adc = process_peak_filter(dev, raw_adc);
    float level_pct = adc_to_percentage(peak_adc, dev->config.adc_min_raw, dev->config.adc_max_raw);

    /* 3. Зчитування та програмний антибрязкот дискретних поплавкових тумблерів */
    bool raw_low = mcu_gpio_read(dev->config.gpio_pin_low_float);
    bool raw_high = mcu_gpio_read(dev->config.gpio_pin_high_float);

    debounce_gpio(raw_low, &dev->debounced_low_state, &dev->raw_low_state,
                  &dev->low_state_change_ms, dev->config.debounce_time_ms, current_time_ms);
    debounce_gpio(raw_high, &dev->debounced_high_state, &dev->raw_high_state,
                  &dev->high_state_change_ms, dev->config.debounce_time_ms, current_time_ms);

    /* 4. Логіка керування помпою та програмний гістерезис */
    if (dev->pump_state != PUMP_STATE_FAULT_DRY_RUN && dev->pump_state != PUMP_STATE_FAULT_OVERRUN) {
        if (dev->config.mode == LIQUID_LEVEL_MODE_FILL) {
            /* Режим наповнення резервуара */
            if (dev->pump_state == PUMP_STATE_OFF) {
                /* Увімкнення за порогом turn_on_pct або спрацьовуванням нижнього поплавка */
                if (level_pct <= dev->config.threshold_turn_on_pct || dev->debounced_low_state) {
                    dev->pump_state = PUMP_STATE_RUNNING;
                    dev->pump_start_time_ms = current_time_ms;
                    dev->initial_pump_level_pct = level_pct;
                    mcu_gpio_write(dev->config.gpio_pin_pump_relay, true);
                }
            } else if (dev->pump_state == PUMP_STATE_RUNNING) {
                /* Вимкнення за порогом turn_off_pct або аварійним верхнім поплавком */
                if (level_pct >= dev->config.threshold_turn_off_pct || dev->debounced_high_state) {
                    dev->pump_state = PUMP_STATE_OFF;
                    mcu_gpio_write(dev->config.gpio_pin_pump_relay, false);
                }
            }
        } else {
            /* Режим відкачування (спорожнення) */
            if (dev->pump_state == PUMP_STATE_OFF) {
                /* Увімкнення за порогом turn_on_pct або верхнім поплавком */
                if (level_pct >= dev->config.threshold_turn_on_pct || dev->debounced_high_state) {
                    dev->pump_state = PUMP_STATE_RUNNING;
                    dev->pump_start_time_ms = current_time_ms;
                    dev->initial_pump_level_pct = level_pct;
                    mcu_gpio_write(dev->config.gpio_pin_pump_relay, true);
                }
            } else if (dev->pump_state == PUMP_STATE_RUNNING) {
                /* Вимкнення за порогом turn_off_pct або нижнім поплавком */
                if (level_pct <= dev->config.threshold_turn_off_pct || dev->debounced_low_state) {
                    dev->pump_state = PUMP_STATE_OFF;
                    mcu_gpio_write(dev->config.gpio_pin_pump_relay, false);
                }
            }
        }
    }

    /* 5. Захисні таймери під час роботи помпи */
    uint32_t running_time = 0;
    if (dev->pump_state == PUMP_STATE_RUNNING) {
        running_time = current_time_ms - dev->pump_start_time_ms;

        /* Перевірка захисту від сухого ходу (відсутність приросту/зменшення рівня за dry_run_timeout_ms) */
        if (running_time >= dev->config.dry_run_timeout_ms) {
            bool dry_run_detected = false;
            if (dev->config.mode == LIQUID_LEVEL_MODE_FILL) {
                /* При наповненні рівень повинен зростати */
                if ((level_pct - dev->initial_pump_level_pct) < 1.0f) {
                    dry_run_detected = true;
                }
            } else {
                /* При відкачуванні рівень повинен знижуватися */
                if ((dev->initial_pump_level_pct - level_pct) < 1.0f) {
                    dry_run_detected = true;
                }
            }

            if (dry_run_detected) {
                dev->pump_state = PUMP_STATE_FAULT_DRY_RUN;
                dev->data.last_fault_time_ms = current_time_ms;
                mcu_gpio_write(dev->config.gpio_pin_pump_relay, false);
            }
        }

        /* Перевірка таймера тривалого перекачування (перевищення max_run_timeout_ms) */
        if (dev->pump_state == PUMP_STATE_RUNNING && running_time >= dev->config.max_run_timeout_ms) {
            dev->pump_state = PUMP_STATE_FAULT_OVERRUN;
            dev->data.last_fault_time_ms = current_time_ms;
            mcu_gpio_write(dev->config.gpio_pin_pump_relay, false);
        }
    }

    /* 6. Оновлення структурних даних телеметрії */
    dev->data.raw_adc = raw_adc;
    dev->data.peak_adc = peak_adc;
    dev->data.level_pct = level_pct;
    dev->data.low_float_active = dev->debounced_low_state;
    dev->data.high_float_active = dev->debounced_high_state;
    dev->data.pump_state = dev->pump_state;
    dev->data.pump_running_time_ms = (dev->pump_state == PUMP_STATE_RUNNING) ? running_time : 0;

    return LIQUID_LEVEL_OK;
}

liquid_level_status_t liquid_level_get_data(const liquid_level_t *dev, liquid_level_data_t *out_data) {
    if (dev == NULL || out_data == NULL) {
        return LIQUID_LEVEL_ERROR_NULL_PTR;
    }
    if (!dev->initialized) {
        return LIQUID_LEVEL_ERROR_PARAM;
    }
    *out_data = dev->data;
    return LIQUID_LEVEL_OK;
}

liquid_level_status_t liquid_level_reset_fault(liquid_level_t *dev) {
    if (dev == NULL) {
        return LIQUID_LEVEL_ERROR_NULL_PTR;
    }
    if (!dev->initialized) {
        return LIQUID_LEVEL_ERROR_PARAM;
    }

    dev->pump_state = PUMP_STATE_OFF;
    dev->pump_start_time_ms = 0;
    dev->initial_pump_level_pct = 0.0f;
    dev->data.pump_state = PUMP_STATE_OFF;
    dev->data.pump_running_time_ms = 0;

    mcu_gpio_write(dev->config.gpio_pin_pump_relay, false);
    return LIQUID_LEVEL_OK;
}

liquid_level_status_t liquid_level_set_mode(liquid_level_t *dev, liquid_level_mode_t mode) {
    if (dev == NULL) {
        return LIQUID_LEVEL_ERROR_NULL_PTR;
    }
    if (!dev->initialized) {
        return LIQUID_LEVEL_ERROR_PARAM;
    }

    dev->config.mode = mode;
    return LIQUID_LEVEL_OK;
}
