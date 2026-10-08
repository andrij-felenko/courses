/**
 * @file mems_capacitive.c
 * @brief Реалізація функцій C-драйвера ємнісного MEMS-сенсора.
 *
 * У даному модулі реалізовано алгоритми синхронного демодулювання сигналів
 * протифазного збудження диференціального конденсатора, ітераційне калібрування
 * зсуву нуля за допомогою ЦАП (DAC) та цифрову фільтрацію вихідних даних.
 */

#include "mems_capacitive.h"
#include <stddef.h>
#include <math.h>

/* Визначення глобального контексту симулятора HAL */
mems_hal_sim_context_t g_mems_hal_sim;

mems_status_t mems_init(mems_dev_t *dev, const mems_config_t *config)
{
    if (!dev || !config) {
        return MEMS_ERR_INVALID_ARG;
    }

    /* Перевірка коректності конфігураційних параметрів */
    if (config->excitation_freq_hz == 0 || config->num_samples_avg == 0 ||
        config->alpha_filter <= 0.0f || config->alpha_filter > 1.0f ||
        config->sensitivity_lsb_per_ff <= 0.0f || config->vref_mv <= 0.0f) {
        return MEMS_ERR_INVALID_ARG;
    }

    /* Очищення контексту пристрою */
    dev->is_initialized = false;
    dev->config = *config;
    dev->dac_zero_offset_raw = 2048U; /* Початковий зсув — середина 12-бітного ЦАП */
    dev->calib_state = MEMS_CALIB_UNINITIALIZED;
    dev->raw_phase_0_accum = 0;
    dev->raw_phase_180_accum = 0;
    dev->diff_voltage_mv = 0.0f;
    dev->capacitance_diff_ff = 0.0f;
    dev->filtered_cap_diff_ff = 0.0f;

    /* Налаштування апаратного рівня HAL */
    mems_hal_config_t hal_cfg = {
        .frequency_hz = config->excitation_freq_hz,
        .dac_resolution_bits = 12,
        .adc_resolution_bits = 12,
        .vref_mv = config->vref_mv
    };

    if (mems_hal_timer_init(&hal_cfg) != MEMS_HAL_OK) {
        return MEMS_ERR_HAL_FAIL;
    }

    /* Установлення початкового значення ЦАП у залізі */
    if (mems_hal_dac_write_raw(dev->dac_zero_offset_raw) != MEMS_HAL_OK) {
        return MEMS_ERR_HAL_FAIL;
    }

    dev->is_initialized = true;
    return MEMS_OK;
}

mems_status_t mems_read_differential_raw(mems_dev_t *dev, int32_t *diff_raw)
{
    if (!dev || !diff_raw) {
        return MEMS_ERR_INVALID_ARG;
    }

    if (!dev->is_initialized) {
        return MEMS_ERR_NOT_INIT;
    }

    int32_t accum_phase_0 = 0;
    int32_t accum_phase_180 = 0;
    uint16_t num_samples = dev->config.num_samples_avg;

    /* Цикл синхронного накопичення вибірок для обох фаз збудження */
    for (uint16_t i = 0; i < num_samples; i++) {
        uint16_t val_0 = 0;
        uint16_t val_180 = 0;

        /* Такт 1: Пряма фаза (Phase 0°) */
        if (mems_hal_set_excitation_phase(MEMS_HAL_PHASE_0) != MEMS_HAL_OK) {
            return MEMS_ERR_HAL_FAIL;
        }
        if (mems_hal_adc_read_sync_phase(MEMS_HAL_PHASE_0, &val_0) != MEMS_HAL_OK) {
            return MEMS_ERR_HAL_FAIL;
        }
        accum_phase_0 += val_0;

        /* Такт 2: Інверсна фаза (Phase 180°) */
        if (mems_hal_set_excitation_phase(MEMS_HAL_PHASE_180) != MEMS_HAL_OK) {
            return MEMS_ERR_HAL_FAIL;
        }
        if (mems_hal_adc_read_sync_phase(MEMS_HAL_PHASE_180, &val_180) != MEMS_HAL_OK) {
            return MEMS_ERR_HAL_FAIL;
        }
        accum_phase_180 += val_180;
    }

    dev->raw_phase_0_accum = accum_phase_0;
    dev->raw_phase_180_accum = accum_phase_180;

    /* Обчислення середніх значень АЦП для обох фаз */
    int32_t avg_0 = accum_phase_0 / num_samples;
    int32_t avg_180 = accum_phase_180 / num_samples;

    /* Різницевий сигнал dV_raw = Phase0 - Phase180 пригнічує постійну складову та 1/f шум */
    *diff_raw = avg_0 - avg_180;

    return MEMS_OK;
}

mems_status_t mems_calibrate_zero(mems_dev_t *dev)
{
    if (!dev) {
        return MEMS_ERR_INVALID_ARG;
    }

    if (!dev->is_initialized) {
        return MEMS_ERR_NOT_INIT;
    }

    dev->calib_state = MEMS_CALIB_IN_PROGRESS;

    /* Активація генерації таккового меандру */
    if (mems_hal_enable_excitation_clk(true) != MEMS_HAL_OK) {
        dev->calib_state = MEMS_CALIB_FAILED;
        return MEMS_ERR_HAL_FAIL;
    }

    /*
     * Алгоритм підбору компенсаційної напруги ЦАП (DAC) методом бінарного пошуку.
     * Шукаємо цифровий код dac_code у діапазоні [0 .. 4095], при якому різниця
     * вихідних відгуків АЦП (Phase0 - Phase180) мінімізується до нуля.
     */
    uint16_t low = 0;
    uint16_t high = 4095;
    uint16_t best_dac = 2048;
    int32_t min_diff_abs = 0x7FFFFFFF;

    /* 12 біт роздільності ЦАП -> 12 кроків ітераційного наближення */
    uint16_t max_steps = (dev->config.calib_max_iterations > 0) ? dev->config.calib_max_iterations : 12;

    for (uint16_t step = 0; step < max_steps; step++) {
        uint16_t mid = low + (high - low) / 2;

        if (mems_hal_dac_write_raw(mid) != MEMS_HAL_OK) {
            dev->calib_state = MEMS_CALIB_FAILED;
            return MEMS_ERR_HAL_FAIL;
        }

        int32_t diff_raw = 0;
        if (mems_read_differential_raw(dev, &diff_raw) != MEMS_OK) {
            dev->calib_state = MEMS_CALIB_FAILED;
            return MEMS_ERR_HAL_FAIL;
        }

        int32_t diff_abs = (diff_raw >= 0) ? diff_raw : -diff_raw;
        if (diff_abs < min_diff_abs) {
            min_diff_abs = diff_abs;
            best_dac = mid;
        }

        /*
         * Напрямок коригування ЦАП:
         * Якщо diff_raw > 0, вихідний потенціал Phase0 вищий за Phase180,
         * отже потрібно коригувати компенсаційну напругу відповідно до напрямку дрейфу.
         */
        if (diff_raw > 0) {
            low = mid + 1;
        } else if (diff_raw < 0) {
            if (mid == 0) break;
            high = mid - 1;
        } else {
            /* Ідеальний баланс досягнуто */
            best_dac = mid;
            break;
        }

        if (low > high) {
            break;
        }
    }

    /* Запис оптимального зсуву ЦАП та перевірка фінального стану */
    dev->dac_zero_offset_raw = best_dac;
    if (mems_hal_dac_write_raw(best_dac) != MEMS_HAL_OK) {
        dev->calib_state = MEMS_CALIB_FAILED;
        return MEMS_ERR_HAL_FAIL;
    }

    /* Перевірочний вимір після встановлення відкаліброваного значення */
    int32_t final_diff = 0;
    if (mems_read_differential_raw(dev, &final_diff) != MEMS_OK) {
        dev->calib_state = MEMS_CALIB_FAILED;
        return MEMS_ERR_HAL_FAIL;
    }

    dev->calib_state = MEMS_CALIB_SUCCESS;
    return MEMS_OK;
}

mems_status_t mems_process_sample(mems_dev_t *dev)
{
    if (!dev) {
        return MEMS_ERR_INVALID_ARG;
    }

    if (!dev->is_initialized) {
        return MEMS_ERR_NOT_INIT;
    }

    int32_t diff_raw = 0;
    mems_status_t status = mems_read_differential_raw(dev, &diff_raw);
    if (status != MEMS_OK) {
        return status;
    }

    /* Перетворення сирого відліку АЦП у різницю напруги в мілівольтах */
    uint32_t max_adc = 4095U;
    float diff_voltage = ((float)diff_raw / (float)max_adc) * dev->config.vref_mv;
    dev->diff_voltage_mv = diff_voltage;

    /* Обчислення фізичної різниці ємностей (dC) у фемтофарадах (fF) */
    float cap_diff_instant = (float)diff_raw / dev->config.sensitivity_lsb_per_ff;
    dev->capacitance_diff_ff = cap_diff_instant;

    /* Експоненціальне усереднення (EMA): Y[n] = alpha * X[n] + (1 - alpha) * Y[n-1] */
    float alpha = dev->config.alpha_filter;
    dev->filtered_cap_diff_ff = (alpha * cap_diff_instant) + ((1.0f - alpha) * dev->filtered_cap_diff_ff);

    return MEMS_OK;
}

mems_status_t mems_get_capacitance_diff(const mems_dev_t *dev, float *cap_diff_ff)
{
    if (!dev || !cap_diff_ff) {
        return MEMS_ERR_INVALID_ARG;
    }
    if (!dev->is_initialized) {
        return MEMS_ERR_NOT_INIT;
    }
    *cap_diff_ff = dev->capacitance_diff_ff;
    return MEMS_OK;
}

mems_status_t mems_get_filtered_capacitance(const mems_dev_t *dev, float *filtered_ff)
{
    if (!dev || !filtered_ff) {
        return MEMS_ERR_INVALID_ARG;
    }
    if (!dev->is_initialized) {
        return MEMS_ERR_NOT_INIT;
    }
    *filtered_ff = dev->filtered_cap_diff_ff;
    return MEMS_OK;
}
