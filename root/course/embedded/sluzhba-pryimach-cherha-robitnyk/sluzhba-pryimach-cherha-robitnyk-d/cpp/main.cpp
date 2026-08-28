#include <iostream>
#include <vector>
#include <span>
#include <chrono>
#include <cstdint>

struct RawPacket {
    std::vector<uint8_t> payload;
    std::chrono::system_clock::time_point t_recv;
};

struct NormalizedEvent {
    uint32_t device_id;
    std::chrono::system_clock::time_point timestamp;
    float temperature_c;
    float humidity_pct;
    float battery_v;
    bool is_valid;
};

class TelemetryWorker {
public:
    static bool process_frame(const RawPacket& raw, NormalizedEvent& out) noexcept {
        // Перевірка розміру (24 байти) та сигнатури 0xAA55
        if (raw.payload.size() < 24 || raw.payload[0] != 0xAA || raw.payload[1] != 0x55) {
            return false;
        }

        // Розпакування Device ID (Big Endian)
        out.device_id = (static_cast<uint32_t>(raw.payload[4]) << 24) |
                        (static_cast<uint32_t>(raw.payload[5]) << 16) |
                        (static_cast<uint32_t>(raw.payload[6]) << 8)  |
                         raw.payload[7];

        // Фіксована кома: температура int16_t (0.01 C)
        int16_t raw_temp = static_cast<int16_t>((raw.payload[12] << 8) | raw.payload[13]);
        out.temperature_c = raw_temp * 0.01f;

        // Вологість uint16_t (0.01 %)
        uint16_t raw_hum = (static_cast<uint16_t>(raw.payload[14]) << 8) | raw.payload[15];
        out.humidity_pct = raw_hum * 0.01f;

        // Батарея uint16_t (1 mV)
        uint16_t raw_vbat = (static_cast<uint16_t>(raw.payload[16]) << 8) | raw.payload[17];
        out.battery_v = raw_vbat * 0.001f;

        out.timestamp = raw.t_recv;

        // Фізична валідація меж
        out.is_valid = (out.temperature_c >= -40.0f && out.temperature_c <= 85.0f) &&
                       (out.humidity_pct >= 0.0f && out.humidity_pct <= 100.0f) &&
                       (out.battery_v >= 2.0f && out.battery_v <= 5.0f);

        return true;
    }
};
