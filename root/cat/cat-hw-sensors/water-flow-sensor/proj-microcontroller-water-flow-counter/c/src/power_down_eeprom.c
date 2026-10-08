#include "power_down_eeprom.h"
#include "water_flow_sensor.h"
#include <string.h>

static power_down_config_t g_pd_config;
static uint32_t g_write_counter = 0;
static bool g_pd_initialized = false;

/* Імітація енергонезалежної пам'яті (EEPROM/Flash) */
static power_down_record_t g_simulated_eeprom_storage;
static bool g_eeprom_has_data = false;

uint16_t power_down_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFFU;
    for (size_t i = 0; i < length; i++) {
        crc ^= ((uint16_t)data[i]) << 8;
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000U) {
                crc = (crc << 1) ^ 0x1021U;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

bool power_down_eeprom_init(const power_down_config_t *config) {
    if (config == NULL) {
        return false;
    }

    g_pd_config = *config;
    g_pd_initialized = true;
    return true;
}

bool power_down_eeprom_save_now(double volume_liters, uint64_t pulse_count) {
    if (!g_pd_initialized) {
        return false;
    }

    power_down_record_t rec;
    rec.magic = POWER_DOWN_MAGIC_HEADER;
    rec.total_volume_liters = volume_liters;
    rec.total_pulse_count = pulse_count;
    rec.write_counter = ++g_write_counter;

    /* Розрахунок CRC16 для всіх полів структури, окрім самого поля crc16 */
    size_t data_len = offsetof(power_down_record_t, crc16);
    rec.crc16 = power_down_crc16((const uint8_t *)&rec, data_len);

    /* Атомарне копіювання в non-volatile пам'ять */
    g_simulated_eeprom_storage = rec;
    g_eeprom_has_data = true;

    return true;
}

void power_down_pvd_isr(void) {
    if (!g_pd_initialized) {
        return;
    }

    /* Швидкий збір поточних метрик без виклику важких функцій */
    water_flow_metrics_t metrics;
    water_flow_sensor_get_metrics(&metrics);

    /* Миттєвий прямомий запис у EEPROM під час знеструмлення */
    power_down_eeprom_save_now(metrics.total_volume_liters, metrics.total_pulse_count);
}

bool power_down_eeprom_restore(double *out_volume_liters, uint64_t *out_pulse_count) {
    if (!g_pd_initialized || out_volume_liters == NULL || out_pulse_count == NULL) {
        return false;
    }

    if (!g_eeprom_has_data) {
        return false; /* Немає збережених даних */
    }

    power_down_record_t rec = g_simulated_eeprom_storage;

    /* Перевірка магічного заголовка */
    if (rec.magic != POWER_DOWN_MAGIC_HEADER) {
        return false;
    }

    /* Верифікація контрольної суми CRC16 */
    size_t data_len = offsetof(power_down_record_t, crc16);
    uint16_t expected_crc = power_down_crc16((const uint8_t *)&rec, data_len);

    if (rec.crc16 != expected_crc) {
        return false; /* Дані пошкоджені */
    }

    *out_volume_liters = rec.total_volume_liters;
    *out_pulse_count = rec.total_pulse_count;
    g_write_counter = rec.write_counter;

    return true;
}
