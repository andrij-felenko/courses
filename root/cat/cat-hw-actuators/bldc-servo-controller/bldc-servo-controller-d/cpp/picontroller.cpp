#include <cmath>

class PiController {
public:
    PiController(float kp, float ki, float i_max, float out_max)
        : kp_(kp), ki_(ki), integrator_(0.0f), i_max_(i_max), out_max_(out_max) {}

    float update(float error, float dt) {
        integrator_ += error * ki_ * dt;
        if (integrator_ > i_max_) integrator_ = i_max_;
        else if (integrator_ < -i_max_) integrator_ = -i_max_;

        float output = error * kp_ + integrator_;
        if (output > out_max_) output = out_max_;
        else if (output < -out_max_) output = -out_max_;
        return output;
    }

    void reset() { integrator_ = 0.0f; }

private:
    float kp_;
    float ki_;
    float integrator_;
    float i_max_;
    float out_max_;
};

struct FocState {
    float i_a{0.0f};
    float i_b{0.0f};
    float theta_e{0.0f};
    float u_alpha{0.0f};
    float u_beta{0.0f};
};

class FocCurrentLoop {
public:
    FocCurrentLoop(const PiController& pi_d, const PiController& pi_q)
        : pi_d_(pi_d), pi_q_(pi_q) {}

    FocState step(float i_a, float i_b, float theta_e, float i_d_target, float i_q_target, float dt) {
        // 1. Пряме перетворення Кларк
        const float i_alpha = i_a;
        const float i_beta = (i_a + 2.0f * i_b) * 0.57735026919f;

        // 2. Пряме перетворення Парка
        const float sin_th = std::sin(theta_e);
        const float cos_th = std::cos(theta_e);

        const float i_d = i_alpha * cos_th + i_beta * sin_th;
        const float i_q = -i_alpha * sin_th + i_beta * cos_th;

        // 3. Обчислення регуляторів струмів d та q
        const float u_d = pi_d_.update(i_d_target - i_d, dt);
        const float u_q = pi_q_.update(i_q_target - i_q, dt);

        // 4. Зворотне перетворення Парка
        FocState state;
        state.i_a = i_a;
        state.i_b = i_b;
        state.theta_e = theta_e;
        state.u_alpha = u_d * cos_th - u_q * sin_th;
        state.u_beta  = u_d * sin_th + u_q * cos_th;
        return state;
    }

private:
    PiController pi_d_;
    PiController pi_q_;
};
