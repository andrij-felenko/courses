#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct {
    uint32_t device_id;
    uint64_t timestamp_ns;
    float temperature_c;
    float humidity_pct;
    float battery_v;
    bool is_valid;
} telemetry_event_t;

bool telemetry_process_frame(const uint8_t *payload, size_t len, uint64_t t_recv_ns, telemetry_event_t *out) {
    if (len < 24 || payload[0] != 0xAA || payload[1] != 0x55) {
        return false;
    }

    out->device_id = ((uint32_t)payload[4] << 24) |
                     ((uint32_t)payload[5] << 16) |
                     ((uint32_t)payload[6] << 8)  |
                      payload[7];

    int16_t raw_temp = (int16_t)(((uint16_t)payload[12] << 8) | payload[13]);
    out->temperature_c = raw_temp * 0.01f;

    uint16_t raw_hum = ((uint16_t)payload[14] << 8) | payload[15];
    out->humidity_pct = raw_hum * 0.01f;

    uint16_t raw_vbat = ((uint16_t)payload[16] << 8) | payload[17];
    out->battery_v = raw_vbat * 0.001f;

    out->timestamp_ns = t_recv_ns;

    out->is_valid = (out->temperature_c >= -40.0f && out->temperature_c <= 85.0f) &&
                    (out->humidity_pct >= 0.0f && out->humidity_pct <= 100.0f) &&
                    (out->battery_v >= 2.0f && out->battery_v <= 5.0f);

    return true;
}
