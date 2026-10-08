#include <algorithm>
#include <cmath>

class PIController {
private:
    float Kp_;
    float Ki_d_;  // Ki * Ts
    float Kbc_;   // Коефіцієнт back-calculation
    float min_out_;
    float max_out_;
    float integrator_{0.0f};

public:
    PIController(float Kp, float Ki, float Ts, float Kbc, float min_out, float max_out)
        : Kp_(Kp), Ki_d_(Ki * Ts), Kbc_(Kbc), min_out_(min_out), max_out_(max_out) {}

    float update(float setpoint, float feedback) {
        float error = setpoint - feedback;
        float p_term = Kp_ * error;
        float u_unsat = p_term + integrator_;

        /* Обмеження виходу насиченням */
        float u_sat = std::clamp(u_unsat, min_out_, max_out_);

        /* Оновлення інтегратора з корекцією anti-windup */
        integrator_ += Ki_d_ * error + Kbc_ * (u_sat - u_unsat);

        return u_sat;
    }

    void reset() {
        integrator_ = 0.0f;
    }
};
