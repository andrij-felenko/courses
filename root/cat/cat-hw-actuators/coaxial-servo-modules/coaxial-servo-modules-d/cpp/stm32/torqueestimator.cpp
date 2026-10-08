#include <cmath>
#include <algorithm>

class TorqueEstimator {
public:
    struct Params {
        float k_t{0.08f};        // Моментна стала, Н·м/А
        float gear_ratio{6.0f};  // Передавальне відношення N
        float efficiency{0.90f}; // ККД редуктора
        float j_ref{0.0036f};    // Зведений момент інерції, кг·м²
        float b_viscous{0.001f}; // Коефіцієнт в'язкого тертя, Н·м·с/рад
        float tau_coulomb{0.05f};// Момент сухого тертя, Н·м
    };

    explicit TorqueEstimator(Params params) : params_(params) {}

    // Обчислення зовнішнього моменту на вихідному валу суглоба
    [[nodiscard]] float estimateExternalTorque(float i_q, float speed_rad_s, float accel_rad_s2) const noexcept {
        const float tau_motor = params_.k_t * i_q;
        const float tau_shaft_raw = tau_motor * params_.gear_ratio * params_.efficiency;
        const float tau_inertia = params_.j_ref * accel_rad_s2;
        const float tau_viscous = params_.b_viscous * speed_rad_s;
        
        float tau_coulomb = 0.0f;
        if (std::abs(speed_rad_s) > 1e-3f) {
            tau_coulomb = (speed_rad_s > 0.0f ? 1.0f : -1.0f) * params_.tau_coulomb;
        }

        return tau_shaft_raw - tau_inertia - tau_viscous - tau_coulomb;
    }

private:
    Params params_;
};
