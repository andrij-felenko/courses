#include <cmath>
#include <iostream>

struct MotorSpecs {
    float j_motor{0.0001f};     // Момент інерції ротора, кг·м²
    float tau_peak_max{1.5f};   // Максимальний піковий момент ротора, Н·м
    float tau_cont_max{0.5f};   // Тривалий момент ротора, Н·м
};

struct LoadRequirements {
    float j_load{0.0036f};      // Момент інерції ланки, кг·м²
    float tau_load_req{8.0f};   // Необхідний момент суглоба, Н·м
    float accel_req{150.0f};    // Необхідне кутове прискорення, рад/с²
};

class InertiaMatchingCalculator {
public:
    struct SelectionResult {
        float optimal_n;
        float inertia_ratio;
        float required_motor_torque;
        bool fits_dynamic_limit;
    };

    static SelectionResult evaluate(const MotorSpecs& motor, const LoadRequirements& load) noexcept {
        const float n_opt = std::sqrt(load.j_load / motor.j_motor);
        const float j_ref = n_opt * n_opt * motor.j_motor;
        const float i_ratio = load.j_load / j_ref;

        // Потрібний момент ротора для подолання інерції ротора та навантаження
        const float tau_m_req = (load.tau_load_req / n_opt) + (motor.j_motor * n_opt * load.accel_req);
        const bool fits = (tau_m_req <= motor.tau_peak_max);

        return {n_opt, i_ratio, tau_m_req, fits};
    }
};
