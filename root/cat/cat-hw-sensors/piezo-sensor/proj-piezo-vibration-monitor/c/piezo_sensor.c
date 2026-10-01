#include "piezo_sensor.h"
#include <stdlib.h>
#include <math.h>

bool piezo_sensor_init(piezo_sensor_t *sensor, const piezo_config_t *config) {
    if (sensor == NULL || config == NULL) {
        return false;
    }

    /* Валідація коефіцієнтів та порогових значень */
    if (config->attack_factor <= 0.0f || config->attack_factor > 1.0f ||
        config->decay_factor <= 0.0f || config->decay_factor > 1.0f ||
        config->energy_alpha <= 0.0f || config->energy_alpha > 1.0f ||
        config->alarm_threshold_high <= config->alarm_threshold_low ||
        config->alarm_threshold_low < 0.0f) {
        return false;
    }

    sensor->config = *config;
    sensor->envelope = 0.0f;
    sensor->energy = 0.0f;
    sensor->peak_count = 0U;
    sensor->alarm_active = false;

    return true;
}

void piezo_sensor_process_sample(piezo_sensor_t *sensor, uint16_t adc_raw) {
    if (sensor == NULL) {
        return;
    }

    /* 1. Центрування сигналу: віднімання зміщення постійної складової та отримання амплітуди */
    int32_t deviation = (int32_t)adc_raw - (int32_t)sensor->config.baseline_adc;
    float abs_signal = (float)labs(deviation);

    /* 2. Обчислення огинаючої з асиметричною фільтрацією (Fast Attack / Slow Decay) */
    if (abs_signal > sensor->envelope) {
        /* При виявленні вихилення огинаюча швидко підтягується до піку */
        sensor->envelope += sensor->config.attack_factor * (abs_signal - sensor->envelope);
    } else {
        /* У паузі між коливаннями огинаюча плавно згасає */
        sensor->envelope -= sensor->config.decay_factor * (sensor->envelope - abs_signal);
    }

    if (sensor->envelope < 0.0f) {
        sensor->envelope = 0.0f;
    }

    /* 3. Обчислення короткочасної енергії впливу (згладжування квадрата амплітуди) */
    float instant_power = abs_signal * abs_signal;
    sensor->energy = sensor->config.energy_alpha * instant_power +
                     (1.0f - sensor->config.energy_alpha) * sensor->energy;

    /* 4. Порогова логіка порівняння з гістерезисом для усунення миготіння тривоги */
    if (!sensor->alarm_active) {
        /* Перехід у стан тривоги при перевищенні верхнього порогу */
        if (sensor->envelope >= sensor->config.alarm_threshold_high) {
            sensor->alarm_active = true;
            sensor->peak_count++;
        }
    } else {
        /* Повернення в норму лише після падіння нижче нижнього порогу */
        if (sensor->envelope < sensor->config.alarm_threshold_low) {
            sensor->alarm_active = false;
        }
    }
}

void piezo_sensor_reset(piezo_sensor_t *sensor) {
    if (sensor == NULL) {
        return;
    }

    sensor->envelope = 0.0f;
    sensor->energy = 0.0f;
    sensor->alarm_active = false;
}

float piezo_sensor_get_envelope(const piezo_sensor_t *sensor) {
    return (sensor != NULL) ? sensor->envelope : 0.0f;
}

float piezo_sensor_get_energy(const piezo_sensor_t *sensor) {
    return (sensor != NULL) ? sensor->energy : 0.0f;
}

bool piezo_sensor_is_alarm_active(const piezo_sensor_t *sensor) {
    return (sensor != NULL) ? sensor->alarm_active : false;
}
