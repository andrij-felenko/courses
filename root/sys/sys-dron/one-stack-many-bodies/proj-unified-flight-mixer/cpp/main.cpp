#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <algorithm>
#include <iomanip>
#include <span>

namespace flight_stack {

enum class ActuatorType {
    Motor,
    Servo,
    Pusher,
    TiltMotor
};

enum class AirframeType {
    Multirotor,
    FixedWing,
    VtolQuadplane,
    VtolTiltrotor,
    RoverDiff
};

struct Vector3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct ActuatorDescriptor {
    ActuatorType type{ActuatorType::Motor};
    Vector3 pos{};          // FRD положення (метри)
    Vector3 dir{0, 0, -1};  // Одиничний вектор тяги
    float c_thrust{1.0f};
    float c_torque{0.0f};
    float min_val{0.0f};
    float max_val{1.0f};
};

struct WrenchSetpoint {
    float f_x{0.0f};
    float f_y{0.0f};
    float f_z{0.0f};
    float m_x{0.0f};
    float m_y{0.0f};
    float m_z{0.0f};
};

struct VehicleState {
    float v_ias{0.0f};     // м/с
    float tilt_rad{0.0f};  // радіани
};

class UnifiedMixer {
public:
    AirframeType airframe_type{AirframeType::Multirotor};
    float v_min{8.0f};
    float v_trans{16.0f};
    std::vector<ActuatorDescriptor> actuators;

    [[nodiscard]] float calculate_transition_weight(float v_ias) const noexcept {
        if (v_ias < v_min) return 0.0f;
        if (v_ias >= v_trans) return 1.0f;
        const float v2 = v_ias * v_ias;
        const float v_min2 = v_min * v_min;
        const float v_trans2 = v_trans * v_trans;
        return (v2 - v_min2) / (v_trans2 - v_min2);
    }

    [[nodiscard]] std::vector<float> mix(const VehicleState& state,
                                         const WrenchSetpoint& sp) const {
        const float v_weight = calculate_transition_weight(state.v_ias);
        std::vector<float> outputs(actuators.size(), 0.0f);

        for (size_t j = 0; j < actuators.size(); ++j) {
            const auto& act = actuators[j];
            float cmd = 0.0f;

            switch (act.type) {
                case ActuatorType::Motor: {
                    const float blend = 1.0f - v_weight;
                    // Підйом по Z + моменти крену, тангажу, рискання
                    cmd += (-sp.f_z) * act.c_thrust * blend;
                    cmd += sp.m_x * act.pos.y * blend;
                    cmd += sp.m_y * (-act.pos.x) * blend;
                    cmd += sp.m_z * act.c_torque * blend;
                    break;
                }
                case ActuatorType::TiltMotor: {
                    const float ct = std::cos(state.tilt_rad);
                    const float st = std::sin(state.tilt_rad);
                    cmd += (-sp.f_z) * ct + sp.f_x * st;
                    cmd += sp.m_x * act.pos.y * ct;
                    cmd += sp.m_y * (-act.pos.x * ct + act.pos.z * st);
                    break;
                }
                case ActuatorType::Pusher: {
                    cmd = sp.f_x * act.c_thrust;
                    break;
                }
                case ActuatorType::Servo: {
                    const float q_scale = 0.1f + 0.9f * v_weight;
                    cmd += (sp.m_x * act.dir.x +
                            sp.m_y * act.dir.y +
                            sp.m_z * act.dir.z) * act.c_thrust * q_scale;
                    break;
                }
            }

            outputs[j] = std::clamp(cmd, act.min_val, act.max_val);
        }

        return outputs;
    }
};

} // namespace flight_stack

int main() {
    using namespace flight_stack;

    UnifiedMixer quadplane;
    quadplane.airframe_type = AirframeType::VtolQuadplane;
    quadplane.v_min = 8.0f;
    quadplane.v_trans = 16.0f;

    // 4 ротори
    const float arms[4][2] = {{0.3f, 0.3f}, {-0.3f, -0.3f}, {0.3f, -0.3f}, {-0.3f, 0.3f}};
    const float dir_torque[4] = {0.05f, 0.05f, -0.05f, -0.05f};

    for (int i = 0; i < 4; ++i) {
        quadplane.actuators.push_back(ActuatorDescriptor{
            .type = ActuatorType::Motor,
            .pos = {arms[i][0], arms[i][1], 0.0f},
            .dir = {0.0f, 0.0f, -1.0f},
            .c_thrust = 1.0f,
            .c_torque = dir_torque[i],
            .min_val = 0.0f,
            .max_val = 1.0f
        });
    }

    // Маршовий двигун
    quadplane.actuators.push_back(ActuatorDescriptor{
        .type = ActuatorType::Pusher,
        .c_thrust = 1.0f,
        .min_val = 0.0f,
        .max_val = 1.0f
    });

    // Елерон, кермо висоти, кермо напрямку
    quadplane.actuators.push_back(ActuatorDescriptor{
        .type = ActuatorType::Servo, .dir = {1.0f, 0.0f, 0.0f}, .min_val = -1.0f, .max_val = 1.0f
    });
    quadplane.actuators.push_back(ActuatorDescriptor{
        .type = ActuatorType::Servo, .dir = {0.0f, 1.0f, 0.0f}, .min_val = -1.0f, .max_val = 1.0f
    });
    quadplane.actuators.push_back(ActuatorDescriptor{
        .type = ActuatorType::Servo, .dir = {0.0f, 0.0f, 1.0f}, .min_val = -1.0f, .max_val = 1.0f
    });

    const WrenchSetpoint setpoint{
        .f_x = 0.6f, .f_z = -1.0f, .m_x = 0.1f, .m_y = 0.0f, .m_z = 0.05f
    };

    std::cout << "=== VTOL QuadPlane C++: Перевірка перехідного режиму ===\n";
    const std::array<float, 6> test_speeds{0.0f, 6.0f, 10.0f, 13.0f, 16.0f, 20.0f};

    for (float speed : test_speeds) {
        VehicleState state{.v_ias = speed, .tilt_rad = 0.0f};
        const auto outputs = quadplane.mix(state, setpoint);
        const float w = quadplane.calculate_transition_weight(speed);

        std::cout << std::fixed << std::setprecision(2)
                  << "V_ias = " << std::setw(4) << speed << " м/с | "
                  << "w_fw = " << std::setw(4) << w << " | "
                  << "Мотор 1: " << outputs[0] << " | "
                  << "Марш: " << outputs[4] << " | "
                  << "Елерон: " << std::showpos << outputs[5] << std::noshowpos
                  << "\n";
    }

    return 0;
}
