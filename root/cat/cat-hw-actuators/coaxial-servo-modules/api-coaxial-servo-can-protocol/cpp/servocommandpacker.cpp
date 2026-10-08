#include <cstdint>
#include <algorithm>
#include <array>

class ServoCommandPacker {
public:
    struct MotionCmd {
        float position; // рад
        float velocity; // рад/с
        float kp;       // Н·м/рад
        float kd;       // Н·м·с/рад
        float torque;   // Н·м
    };

    static std::array<uint8_t, 8> packMIT(const MotionCmd& cmd) {
        std::array<uint8_t, 8> payload{};

        uint16_t p_int  = floatToUint(cmd.position, -12.5f,  12.5f, 16);
        uint16_t v_int  = floatToUint(cmd.velocity, -30.0f,  30.0f, 12);
        uint16_t kp_int = floatToUint(cmd.kp,         0.0f, 500.0f, 12);
        uint16_t kd_int = floatToUint(cmd.kd,         0.0f,   5.0f, 12);
        uint16_t t_int  = floatToUint(cmd.torque,   -12.0f,  12.0f, 12);

        payload[0] = static_cast<uint8_t>(p_int >> 8);
        payload[1] = static_cast<uint8_t>(p_int & 0xFF);
        payload[2] = static_cast<uint8_t>(v_int >> 4);
        payload[3] = static_cast<uint8_t>(((v_int & 0x0F) << 4) | (kp_int >> 8));
        payload[4] = static_cast<uint8_t>(kp_int & 0xFF);
        payload[5] = static_cast<uint8_t>(kd_int >> 4);
        payload[6] = static_cast<uint8_t>(((kd_int & 0x0F) << 4) | (t_int >> 8));
        payload[7] = static_cast<uint8_t>(t_int & 0xFF);

        return payload;
    }

private:
    static uint16_t floatToUint(float val, float min_val, float max_val, uint8_t bits) {
        val = std::clamp(val, min_val, max_val);
        float span = max_val - min_val;
        uint32_t max_int = (1U << bits) - 1U;
        return static_cast<uint16_t>(((val - min_val) / span) * static_cast<float>(max_int));
    }
};
