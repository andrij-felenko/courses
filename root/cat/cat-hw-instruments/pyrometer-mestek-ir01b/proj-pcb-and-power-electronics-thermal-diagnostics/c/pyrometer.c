#include "pyrometer.h"
#include <math.h>

float pyro_celsius_to_kelvin(float celsius) {
    return celsius - ABSOLUTE_ZERO_CELSIUS;
}

float pyro_kelvin_to_celsius(float kelvin) {
    return kelvin + ABSOLUTE_ZERO_CELSIUS;
}

pyro_status_t pyro_init_config(pyro_config_t *config) {
    if (config == NULL) {
        return PYRO_ERR_SENSOR_FAULT;
    }

    config->emissivity = 0.95f;
    config->bg_temp_celsius = 25.0f;
    config->k_sensor = 1.25e-11f;
    config->high_alarm_celsius = 100.0f;
    config->low_alarm_celsius = 0.0f;
    config->hysteresis_celsius = 1.5f;

    return PYRO_OK;
}

pyro_status_t pyro_update_alarms(
    const pyro_config_t *config,
    pyro_reading_t *reading
) {
    if (config == NULL || reading == NULL) {
        return PYRO_ERR_SENSOR_FAULT;
    }

    float t = reading->object_temp_celsius;

    /* Логіка верхньої тривоги HAL з гістерезисом */
    if (reading->high_alarm_active) {
        if (t < (config->high_alarm_celsius - config->hysteresis_celsius)) {
            reading->high_alarm_active = false;
        }
    } else {
        if (t >= config->high_alarm_celsius) {
            reading->high_alarm_active = true;
        }
    }

    /* Логіка нижньої тривоги LAL з гістерезисом */
    if (reading->low_alarm_active) {
        if (t > (config->low_alarm_celsius + config->hysteresis_celsius)) {
            reading->low_alarm_active = false;
        }
    } else {
        if (t <= config->low_alarm_celsius) {
            reading->low_alarm_active = true;
        }
    }

    /* Встановлення статусних прапорців */
    if (reading->high_alarm_active) {
        reading->status = PYRO_WARN_HIGH_ALARM;
    } else if (reading->low_alarm_active) {
        reading->status = PYRO_WARN_LOW_ALARM;
    } else {
        reading->status = PYRO_OK;
    }

    return reading->status;
}

pyro_status_t pyro_calculate_temperature(
    const pyro_config_t *config,
    float raw_voltage_v,
    float ambient_temp_celsius,
    pyro_reading_t *reading
) {
    if (config == NULL || reading == NULL) {
        return PYRO_ERR_SENSOR_FAULT;
    }

    /* Перевірка валідності емісивності */
    if (config->emissivity < PYRO_MIN_EMISSIVITY || config->emissivity > PYRO_MAX_EMISSIVITY) {
        reading->status = PYRO_ERR_INVALID_EMISSIVITY;
        return PYRO_ERR_INVALID_EMISSIVITY;
    }

    if (config->k_sensor <= 0.0f) {
        reading->status = PYRO_ERR_SENSOR_FAULT;
        return PYRO_ERR_SENSOR_FAULT;
    }

    reading->raw_voltage_mv = raw_voltage_v * 1000.0f;
    reading->ambient_temp_celsius = ambient_temp_celsius;

    /* Перетворення температур у Кельвіни */
    float t_amb_k = pyro_celsius_to_kelvin(ambient_temp_celsius);
    float t_bg_k = pyro_celsius_to_kelvin(config->bg_temp_celsius);

    /* Четверті степені температур */
    float t_amb_4 = t_amb_k * t_amb_k * t_amb_k * t_amb_k;
    float t_bg_4 = t_bg_k * t_bg_k * t_bg_k * t_bg_k;

    /* Закон Стефана — Больцмана з урахуванням емісивності та фонового відбиття */
    float term_voltage = raw_voltage_v / config->k_sensor;
    float term_bg_reflected = (1.0f - config->emissivity) * t_bg_4;
    float t_obj_4_val = (term_voltage + t_amb_4 - term_bg_reflected) / config->emissivity;

    if (t_obj_4_val <= 0.0f) {
        reading->status = PYRO_ERR_SENSOR_FAULT;
        return PYRO_ERR_SENSOR_FAULT;
    }

    float t_obj_k = powf(t_obj_4_val, 0.25f);
    float t_obj_c = pyro_kelvin_to_celsius(t_obj_k);

    reading->object_temp_celsius = t_obj_c;

    /* Перевірка виходу за межі діапазону вимірювача MESTEK IR01B */
    if (t_obj_c < PYRO_MIN_TEMP_CELSIUS) {
        reading->status = PYRO_ERR_OUT_OF_RANGE_LOW;
        return PYRO_ERR_OUT_OF_RANGE_LOW;
    }

    if (t_obj_c > PYRO_MAX_TEMP_CELSIUS) {
        reading->status = PYRO_ERR_OUT_OF_RANGE_HIGH;
        return PYRO_ERR_OUT_OF_RANGE_HIGH;
    }

    /* Оновлення аварійних індикаторів з урахуванням гістерезису */
    pyro_update_alarms(config, reading);

    return reading->status;
}
