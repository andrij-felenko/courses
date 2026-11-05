#include "tank_gauge.h"
#include <string.h>
#include <math.h>

#define TANK_GAUGE_MAGIC 0x5447 /* "TG" */

static void insertion_sort(float *arr, uint8_t n) {
    for (uint8_t i = 1; i < n; i++) {
        float key = arr[i];
        int32_t j = i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

uint16_t tank_gauge_calc_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i];
        for (uint8_t b = 0; b < 8; b++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}

bool tank_gauge_init(tank_gauge_t *gauge, uint8_t window_size, float sensor_height_mm, float max_volume_liters) {
    if (!gauge || window_size == 0 || window_size > TANK_GAUGE_MEDIAN_WINDOW_MAX) {
        return false;
    }
    memset(gauge, 0, sizeof(*gauge));
    gauge->window_size = window_size;
    gauge->config.magic = TANK_GAUGE_MAGIC;
    gauge->config.sensor_height_mm = sensor_height_mm;
    gauge->config.max_volume_liters = max_volume_liters;
    gauge->config.num_points = 0;
    return true;
}

bool tank_gauge_add_calib_point(tank_gauge_t *gauge, float height_mm, float volume_liters) {
    if (!gauge || gauge->config.num_points >= TANK_GAUGE_MAX_CALIB_POINTS) {
        return false;
    }
    uint16_t idx = gauge->config.num_points;
    gauge->config.points[idx].height_mm = height_mm;
    gauge->config.points[idx].volume_liters = volume_liters;
    gauge->config.num_points++;
    return true;
}

float tank_gauge_sound_speed(float temperature_c) {
    /* Напівемпірична формула швидкості звуку в сухому повітрі: c(T) = 331.3 + 0.606 * T */
    return 331.3f + 0.606f * temperature_c;
}

float tank_gauge_calc_distance_mm(uint32_t tof_us, float temperature_c) {
    float speed_m_s = tank_gauge_sound_speed(temperature_c);
    /* d = (c * t) / 2; t у мікросекундах: t * 1e-6 с, переведення у мм: * 1000 */
    /* d_mm = (speed_m_s * tof_us * 0.001f) / 2.0f = speed_m_s * tof_us * 0.0005f */
    return speed_m_s * (float)tof_us * 0.0005f;
}

float tank_gauge_filter_distance(tank_gauge_t *gauge, float new_distance_mm) {
    if (!gauge) return new_distance_mm;

    gauge->window[gauge->head] = new_distance_mm;
    gauge->head = (gauge->head + 1) % gauge->window_size;
    if (gauge->count < gauge->window_size) {
        gauge->count++;
    }

    float sorted[TANK_GAUGE_MEDIAN_WINDOW_MAX];
    memcpy(sorted, gauge->window, sizeof(float) * gauge->count);
    insertion_sort(sorted, gauge->count);

    if (gauge->count % 2 == 1) {
        return sorted[gauge->count / 2];
    } else {
        return (sorted[(gauge->count / 2) - 1] + sorted[gauge->count / 2]) * 0.5f;
    }
}

float tank_gauge_calc_level_height_mm(const tank_gauge_t *gauge, float filtered_distance_mm) {
    if (!gauge) return 0.0f;
    float level = gauge->config.sensor_height_mm - filtered_distance_mm;
    if (level < 0.0f) level = 0.0f;
    if (level > gauge->config.sensor_height_mm) level = gauge->config.sensor_height_mm;
    return level;
}

float tank_gauge_height_to_volume(const tank_gauge_t *gauge, float height_mm) {
    if (!gauge || gauge->config.num_points == 0) return 0.0f;

    const tank_gauge_eeprom_config_t *cfg = &gauge->config;

    /* Нижче першої точки */
    if (height_mm <= cfg->points[0].height_mm) {
        return cfg->points[0].volume_liters;
    }

    /* Вище останньої точки */
    if (height_mm >= cfg->points[cfg->num_points - 1].height_mm) {
        return cfg->points[cfg->num_points - 1].volume_liters;
    }

    /* Кусочно-лінійна інтерполяція між сусідніми вузлами */
    for (uint16_t i = 0; i < cfg->num_points - 1; i++) {
        float h0 = cfg->points[i].height_mm;
        float h1 = cfg->points[i + 1].height_mm;
        if (height_mm >= h0 && height_mm <= h1) {
            float v0 = cfg->points[i].volume_liters;
            float v1 = cfg->points[i + 1].volume_liters;
            float t = (height_mm - h0) / (h1 - h0);
            return v0 + t * (v1 - v0);
        }
    }

    return 0.0f;
}

float tank_gauge_volume_to_percent(const tank_gauge_t *gauge, float volume_liters) {
    if (!gauge || gauge->config.max_volume_liters <= 0.0f) return 0.0f;
    float pct = (volume_liters / gauge->config.max_volume_liters) * 100.0f;
    if (pct < 0.0f) pct = 0.0f;
    if (pct > 100.0f) pct = 100.0f;
    return pct;
}

bool tank_gauge_validate_config(const tank_gauge_eeprom_config_t *cfg) {
    if (!cfg) return false;
    if (cfg->magic != TANK_GAUGE_MAGIC) return false;
    if (cfg->num_points < 2 || cfg->num_points > TANK_GAUGE_MAX_CALIB_POINTS) return false;

    uint16_t expected_crc = tank_gauge_calc_crc16((const uint8_t *)cfg, sizeof(*cfg) - sizeof(cfg->crc16));
    return (cfg->crc16 == expected_crc);
}
