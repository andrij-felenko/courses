#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    uint16_t magic;
    uint16_t sensor_id;
    float temperature;
    float pressure;
    uint32_t checksum;
} TelemetryPacket;

bool parse_telemetry_c(const uint8_t* buffer, size_t len, TelemetryPacket* out) {
    if (len < sizeof(TelemetryPacket) || !out) {
        return false;
    }
    // Копіювання захищає від порушення вирівнювання (unaligned memory access)
    memcpy(out, buffer, sizeof(TelemetryPacket));
    return out->magic == 0xAA55;
}
