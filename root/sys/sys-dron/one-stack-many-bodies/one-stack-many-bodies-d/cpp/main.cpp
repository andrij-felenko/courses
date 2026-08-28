#include <array>
#include <span>
#include <cmath>
#include <algorithm>

namespace flight_stack {

enum class AirframeClass : uint8_t {
    MultirotorX4,
    FixedWingConventional,
    VtolQuadplane,
    VtolTiltrotor,
    RoverSkidSteer
};

struct WrenchCommand {
    float fx{0.0f}, fy{0.0f}, fz{0.0f};
    float mx{0.0f}, my{0.0f}, mz{0.0f};
};

struct AirframeState {
    float v_ias{0.0f};
    float tilt_angle{0.0f};
    float dynamic_pressure{0.0f};
};

struct ActuatorChannel {
    uint8_t output_channel{0};
    std::array<float, 3> pos{0.0f, 0.0f, 0.0f};
    std::array<float, 3> dir{0.0f, 0.0f, -1.0f};
    float c_thrust{1.0f};
    float c_torque{0.0f};
    float min_limit{0.0f};
    float max_limit{1.0f};
};

class UniversalControlAllocator {
public:
    static constexpr size_t max_channels = 16;

    static void allocate(AirframeClass airframe,
                         const AirframeState& state,
                         const WrenchCommand& wrench,
                         std::span<const ActuatorChannel> actuators,
                         std::span<float> out_commands) noexcept {
        const size_t n = std::min(actuators.size(), out_commands.size());

        for (size_t i = 0; i < n; ++i) {
            const auto& act = actuators[i];
            float raw_cmd = 0.0f;

            // Базовий розподіл сил і моментів з урахуванням геометрії
            raw_cmd += -wrench.fz * (-act.dir[2]);
            raw_cmd += wrench.mx * act.pos[1];
            raw_cmd += wrench.my * (-act.pos[0]);
            raw_cmd += wrench.mz * act.c_torque;

            // Пріоритетна десатурація
            out_commands[i] = std::clamp(raw_cmd, act.min_limit, act.max_limit);
        }
    }
};

} // namespace flight_stack
