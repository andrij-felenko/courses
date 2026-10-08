#include <cstdint>
#include <array>

struct PhysicalTelemetry {
    int32_t positionCounts{0};
    float velocityRpm{0.0f};
    float currentAmps{0.0f};
    float voltageVolts{0.0f};
    float temperatureCelsius{0.0f};
};

class TelemetryDecoder {
public:
    static PhysicalTelemetry decode(const std::array<uint8_t, 12>& bytes) {
        PhysicalTelemetry data;
        
        int32_t rawPos = static_cast<int32_t>(bytes[0] | (bytes[1] << 8) | (bytes[2] << 16) | (bytes[3] << 24));
        int16_t rawVel = static_cast<int16_t>(bytes[4] | (bytes[5] << 8));
        int16_t rawCurr = static_cast<int16_t>(bytes[6] | (bytes[7] << 8));
        uint16_t rawVolt = static_cast<uint16_t>(bytes[8] | (bytes[9] << 8));
        int16_t rawTemp = static_cast<int16_t>(bytes[10] | (bytes[11] << 8));

        data.positionCounts = rawPos;
        data.velocityRpm = static_cast<float>(rawVel);
        data.currentAmps = static_cast<float>(rawCurr) / 1000.0f;
        data.voltageVolts = static_cast<float>(rawVolt) / 1000.0f;
        data.temperatureCelsius = static_cast<float>(rawTemp) / 10.0f;

        return data;
    }
};
