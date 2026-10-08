#include <cstdint>
#include <array>

struct ServoTelemetry {
    uint8_t motorId;
    float position; // рад
    float velocity; // рад/с
    float torque;   // Н·м
    float tempC;    // °C
    uint8_t errorCode;
};

class ServoTelemetryUnpacker {
public:
    static ServoTelemetry unpack(const std::array<uint8_t, 8>& payload) {
        ServoTelemetry telemetry{};
        telemetry.motorId = payload[0];

        uint16_t p_int = (static_cast<uint16_t>(payload[1]) << 8) | payload[2];
        uint16_t v_int = (static_cast<uint16_t>(payload[3]) << 4) | (payload[4] >> 4);
        uint16_t t_int = ((static_cast<uint16_t>(payload[4]) & 0x0F) << 8) | payload[5];

        telemetry.position  = uintToFloat(p_int, -12.5f, 12.5f, 16);
        telemetry.velocity  = uintToFloat(v_int, -30.0f, 30.0f, 12);
        telemetry.torque    = uintToFloat(t_int, -12.0f, 12.0f, 12);
        telemetry.tempC     = static_cast<float>(payload[6]);
        telemetry.errorCode = payload[7];

        return telemetry;
    }

private:
    static float uintToFloat(uint16_t intVal, float minVal, float maxVal, uint8_t bits) {
        uint32_t maxInt = (1U << bits) - 1U;
        float span = maxVal - minVal;
        return minVal + (static_cast<float>(intVal) / static_cast<float>(maxInt)) * span;
    }
};
