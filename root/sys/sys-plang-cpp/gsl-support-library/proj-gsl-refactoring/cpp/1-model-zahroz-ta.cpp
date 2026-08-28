#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <vector>

struct TelemetryRecord {
    uint16_t sensor_id;
    uint32_t timestamp;
    double*  readings;
    int      reading_count;
};

// Застаріла C++ функція у стилі "C з класами"
int parse_telemetry_packet_legacy(const uint8_t* raw_buffer, int buffer_size,
                                 TelemetryRecord** out_record, void* logger_ctx) {
    if (!raw_buffer || buffer_size < 12) {
        return -1;
    }

    uint32_t magic = *reinterpret_cast<const uint32_t*>(raw_buffer);
    if (magic != 0x54454C4D) {
        return -2;
    }

    uint16_t sensor_id = *reinterpret_cast<const uint16_t*>(raw_buffer + 4);
    uint16_t payload_len = *reinterpret_cast<const uint16_t*>(raw_buffer + 6);
    uint32_t timestamp = *reinterpret_cast<const uint32_t*>(raw_buffer + 8);

    if (buffer_size < 12 + payload_len + 4) {
        return -3;
    }

    TelemetryRecord* rec = new (std::nothrow) TelemetryRecord();
    if (!rec) return -4;

    rec->sensor_id = sensor_id;
    rec->timestamp = timestamp;
    rec->reading_count = payload_len / sizeof(double);
    rec->readings = nullptr;

    if (rec->reading_count > 0) {
        rec->readings = new (std::nothrow) double[rec->reading_count];
        if (!rec->readings) {
            delete rec;
            return -4;
        }
        std::memcpy(rec->readings, raw_buffer + 12, rec->reading_count * sizeof(double));
    }

    *out_record = rec;
    return 0;
}
