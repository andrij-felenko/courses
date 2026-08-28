#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    int16_t temperature_centi_c;
    uint16_t pressure_deci_hpa;
    uint16_t voltage_mv;
    uint8_t flags;
} sensor_data_t;

// Безпечне розпакування Little-Endian без порушення Strict Aliasing та вирівнювання
bool unpack_telemetry_payload(const uint8_t *payload, size_t len, sensor_data_t *out) {
    if (len < 8 || out == NULL || payload == NULL) {
        return false;
    }

    // Явне збирання цілих чисел по байтах
    out->temperature_centi_c = (int16_t)((uint16_t)payload[0] | ((uint16_t)payload[1] << 8));
    out->pressure_deci_hpa   = (uint16_t)payload[2] | ((uint16_t)payload[3] << 8);
    out->voltage_mv          = (uint16_t)payload[4] | ((uint16_t)payload[5] << 8);
    out->flags               = payload[6];
    // payload[7] — резервний байт вирівнювання, ігнорується

    return true;
}

// Безпечне пакування Little-Endian у вихідний буфер
size_t pack_telemetry_payload(const sensor_data_t *in, uint8_t *out_payload, size_t max_len) {
    if (max_len < 8 || in == NULL || out_payload == NULL) {
        return 0;
    }

    out_payload[0] = (uint8_t)(in->temperature_centi_c & 0xFF);
    out_payload[1] = (uint8_t)((in->temperature_centi_c >> 8) & 0xFF);
    out_payload[2] = (uint8_t)(in->pressure_deci_hpa & 0xFF);
    out_payload[3] = (uint8_t)((in->pressure_deci_hpa >> 8) & 0xFF);
    out_payload[4] = (uint8_t)(in->voltage_mv & 0xFF);
    out_payload[5] = (uint8_t)((in->voltage_mv >> 8) & 0xFF);
    out_payload[6] = in->flags;
    out_payload[7] = 0x00; // Резерв завжди занулюється

    return 8;
}
