#include "opm_sensor.h"
#include <math.h>

/**
 * @brief Внутрішня функція лінійної інтерполяції Rλ за довжиною хвилі.
 */
static opm_status_t interpolate_sensitivity(const opm_calib_table_t *table, uint16_t wavelength_nm, float *out_r_lambda) {
    if (!table || !table->points || table->count == 0 || !out_r_lambda) {
        return OPM_ERR_INVALID_PARAM;
    }

    /* Перевірка меж калібрувальної таблиці */
    if (wavelength_nm < table->points[0].wavelength_nm || 
        wavelength_nm > table->points[table->count - 1].wavelength_nm) {
        return OPM_ERR_WAVELENGTH_OUT_OF_RANGE;
    }

    /* Точний збіг з першою точкою */
    if (wavelength_nm == table->points[0].wavelength_nm) {
        *out_r_lambda = table->points[0].sensitivity_a_w;
        return OPM_OK;
    }

    /* Пошук інтервалу для інтерполяції */
    for (size_t i = 0; i < table->count - 1; i++) {
        uint16_t w0 = table->points[i].wavelength_nm;
        uint16_t w1 = table->points[i + 1].wavelength_nm;

        if (wavelength_nm >= w0 && wavelength_nm <= w1) {
            float r0 = table->points[i].sensitivity_a_w;
            float r1 = table->points[i + 1].sensitivity_a_w;
            
            /* Формула лінійної інтерполяції: R(λ) = R0 + (R1 - R0) * (λ - λ0) / (λ1 - λ0) */
            float slope = (r1 - r0) / (float)(w1 - w0);
            *out_r_lambda = r0 + slope * (float)(wavelength_nm - w0);
            return OPM_OK;
        }
    }

    return OPM_ERR_WAVELENGTH_OUT_OF_RANGE;
}

opm_status_t opm_init(opm_sensor_t *sensor, const opm_config_t *config, const opm_calib_table_t *calib_table) {
    if (!sensor || !config || !calib_table || calib_table->count == 0) {
        return OPM_ERR_INVALID_PARAM;
    }

    sensor->config = *config;
    sensor->calib_table = *calib_table;
    sensor->dark_offset_v = 0.0f;
    sensor->filter_index = 0;
    sensor->filter_count = 0;
    sensor->current_wavelength_nm = 0;
    sensor->current_sensitivity_a_w = 0.0f;
    sensor->is_initialized = true;

    /* Встановлення першої доступної довжини хвилі за замовчуванням */
    return opm_set_wavelength(sensor, calib_table->points[0].wavelength_nm);
}

opm_status_t opm_calibrate_dark_offset(opm_sensor_t *sensor, const uint16_t *raw_samples, size_t sample_count) {
    if (!sensor || !sensor->is_initialized || !raw_samples || sample_count == 0) {
        return OPM_ERR_INVALID_PARAM;
    }

    uint64_t sum_adc = 0;
    for (size_t i = 0; i < sample_count; i++) {
        sum_adc += raw_samples[i];
    }

    float avg_adc = (float)sum_adc / (float)sample_count;
    /* Перетворення середніх відліків АЦП у напругу темнового зсуву */
    sensor->dark_offset_v = (avg_adc / (float)sensor->config.adc_max_count) * sensor->config.adc_vref_v;

    return OPM_OK;
}

opm_status_t opm_set_wavelength(opm_sensor_t *sensor, uint16_t wavelength_nm) {
    if (!sensor || !sensor->is_initialized) {
        return OPM_ERR_NOT_INITIALIZED;
    }

    float r_lambda = 0.0f;
    opm_status_t status = interpolate_sensitivity(&sensor->calib_table, wavelength_nm, &r_lambda);
    if (status != OPM_OK) {
        return status;
    }

    sensor->current_wavelength_nm = wavelength_nm;
    sensor->current_sensitivity_a_w = r_lambda;
    return OPM_OK;
}

opm_status_t opm_process_adc_sample(opm_sensor_t *sensor, uint16_t raw_adc_sample, float *out_power_w, float *out_power_dbm) {
    if (!sensor || !sensor->is_initialized || !out_power_w || !out_power_dbm) {
        return OPM_ERR_INVALID_PARAM;
    }

    /* Оновлення кільцевого буфера ковзного усереднення */
    sensor->filter_buffer[sensor->filter_index] = raw_adc_sample;
    sensor->filter_index = (sensor->filter_index + 1) % OPM_FILTER_WINDOW_SIZE;
    if (sensor->filter_count < OPM_FILTER_WINDOW_SIZE) {
        sensor->filter_count++;
    }

    /* Обчислення усередненого значення АЦП */
    uint32_t sum_adc = 0;
    for (size_t i = 0; i < sensor->filter_count; i++) {
        sum_adc += sensor->filter_buffer[i];
    }
    float filtered_adc = (float)sum_adc / (float)sensor->filter_count;

    /* 1. Розрахунок повної вихідної напруги TIA */
    float raw_voltage = (filtered_adc / (float)sensor->config.adc_max_count) * sensor->config.adc_vref_v;

    /* 2. Компенсація темнового струму */
    float signal_voltage = raw_voltage - sensor->dark_offset_v;
    if (signal_voltage < 0.0f) {
        signal_voltage = 0.0f;
    }

    /* 3. Перетворення напруги у фотострум I_ph = V_sig / Rf */
    float photocurrent_a = signal_voltage / sensor->config.tia_gain_ohm;

    /* 4. Обчислення оптичної потужності P = I_ph / R(λ) */
    float power_w = photocurrent_a / sensor->current_sensitivity_a_w;
    *out_power_w = power_w;
    *out_power_dbm = opm_watts_to_dbm(power_w);

    /* 5. Перевірка перевищення порогу оптичного руйнування LIDT */
    if (power_w >= sensor->config.lidt_max_power_w) {
        return OPM_ERR_LIDT_EXCEEDED;
    }

    return OPM_OK;
}

float opm_watts_to_dbm(float power_w) {
    if (power_w <= 1e-15f) {
        return -120.0f; /* Нижня межа для нульового/надмалого сигналу */
    }
    /* P(dBm) = 10 * log10(P(W) / 1mW) */
    return 10.0f * log10f(power_w / 0.001f);
}
