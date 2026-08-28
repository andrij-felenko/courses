#include <cstdint>
#include <algorithm>

namespace control {

struct PidConfig {
    float kp{0.0f};
    float ki{0.0f};
    float kd{0.0f};
    float kff{0.0f};
    float out_min{-1.0f};
    float out_max{1.0f};
    float i_min{-1.0f};
    float i_max{1.0f};
    float slew_rate_max{0.0f}; // [од/с]
};

struct PidTelemetry {
    float setpoint{0.0f};
    float measurement{0.0f};
    float error{0.0f};
    float p_term{0.0f};
    float i_term{0.0f};
    float d_term{0.0f};
    float ff_term{0.0f};
    float output{0.0f};
    bool  is_saturated{false};
};

} // namespace control
