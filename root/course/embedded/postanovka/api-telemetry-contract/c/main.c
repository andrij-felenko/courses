#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TELEMETRY_MAGIC 0xA55A
#define TELEMETRY_VERSION 1
#define TELEMETRY_FRAME_SIZE 24

typedef struct __attribute__((packed)) {
    uint16_t magic;
    uint8_t version;
    uint8_t flags;
    uint32_t node_id;
    uint32_t seq_num;
    uint32_t timestamp;
    int16_t temperature;
    uint16_t humidity;
    uint16_t battery_mv;
    uint16_t crc16;
} telemetry_frame_raw_t;

typedef struct {
    uint32_t node_id;
    uint32_t seq_num;
    uint32_t timestamp;
    float temperature_c;
    float humidity_pct;
    float battery_v;
    bool low_battery;
    bool sensor_fault;
    bool tamper;
    bool offline_sync;
} telemetry_parsed_t;

static uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int j = 0; j < 8; ++j) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

bool telemetry_parse(const uint8_t *buf, size_t len, telemetry_parsed_t *out) {
    if (!buf || len < TELEMETRY_FRAME_SIZE || !out) {
        return false;
    }

    const telemetry_frame_raw_t *raw = (const telemetry_frame_raw_t *)buf;

    if (raw->magic != TELEMETRY_MAGIC || raw->version != TELEMETRY_VERSION) {
        return false;
    }

    uint16_t expected_crc = crc16_ccitt(buf, TELEMETRY_FRAME_SIZE - 2);
    if (raw->crc16 != expected_crc) {
        return false;
    }

    out->node_id = raw->node_id;
    out->seq_num = raw->seq_num;
    out->timestamp = raw->timestamp;
    out->temperature_c = (float)raw->temperature / 100.0f;
    out->humidity_pct = (float)raw->humidity / 100.0f;
    out->battery_v = (float)raw->battery_mv / 1000.0f;

    out->low_battery = (raw->flags & (1 << 0)) != 0;
    out->sensor_fault = (raw->flags & (1 << 1)) != 0;
    out->tamper = (raw->flags & (1 << 2)) != 0;
    out->offline_sync = (raw->flags & (1 << 3)) != 0;

    return true;
}
