#include <array>
#include <cmath>
#include <cstdint>
#include <span>

class EkfDeadReckoning {
public:
    static constexpr size_t kStateDim = 9;
    static constexpr float kGravity = 9.81f;

    struct State {
        float px{0.0f}, py{0.0f}, pz{0.0f};             // Позиція NED (м)
        float vx{0.0f}, vy{0.0f}, vz{0.0f};             // Швидкість NED (м/с)
        float bax{0.0f}, bay{0.0f}, baz{0.0f};          // Зсув акселерометра (м/с²)
    };

    EkfDeadReckoning() {
        reset();
    }

    void reset() noexcept {
        x_.fill(0.0f);
        P_.fill(0.0f);

        // Початкові дисперсії стану
        for (size_t i = 0; i < 3; ++i) P_[i] = 1.0f;
        for (size_t i = 3; i < 6; ++i) P_[i] = 0.01f;
        for (size_t i = 6; i < 9; ++i) P_[i] = 0.0025f;
    }

    // Передбачення стану за даними IMU
    void predict(std::span<const float, 3> a_body,
                 const std::array<std::array<float, 3>, 3>& R_wb,
                 float dt) noexcept
    {
        std::array<float, 3> a_unbiased{
            a_body[0] - x_[6],
            a_body[1] - x_[7],
            a_body[2] - x_[8]
        };

        // Трансформація у світову систему NED
        std::array<float, 3> a_world{0.0f, 0.0f, 0.0f};
        for (size_t i = 0; i < 3; ++i) {
            for (size_t j = 0; j < 3; ++j) {
                a_world[i] += R_wb[i][j] * a_unbiased[j];
            }
        }
        a_world[2] += kGravity;

        const float dt2 = 0.5f * dt * dt;
        for (size_t i = 0; i < 3; ++i) {
            x_[i]     += x_[3 + i] * dt + a_world[i] * dt2;
            x_[3 + i] += a_world[i] * dt;
        }

        // Екстраполяція коваріацій
        for (size_t i = 0; i < 3; ++i) {
            P_[i]     += (2.0f * P_[3 + i] * dt + q_pos_) * dt;
            P_[3 + i] += q_vel_ * dt;
            P_[6 + i] += q_bias_ * dt;
        }
    }

    // Корекція швидкості оптичним потоком
    [[nodiscard]] bool updateOpticalFlow(float vx_meas, float vy_meas, float r_cov, float gate_limit = 4.0f) noexcept {
        const std::array<float, 2> z{vx_meas, vy_meas};

        for (size_t axis = 0; axis < 2; ++axis) {
            const size_t v_idx = 3 + axis;
            const float y = z[axis] - x_[v_idx];
            const float S = P_[v_idx] + r_cov;

            // Тест Махаланобіса на відкидання викидів
            if ((y * y) / S > gate_limit) {
                return false;
            }

            const float K = P_[v_idx] / S;
            x_[v_idx] += K * y;

            const size_t b_idx = 6 + axis;
            const float K_bias = P_[b_idx] / S;
            x_[b_idx] -= K_bias * (y * 0.1f);

            P_[v_idx] *= (1.0f - K);
        }
        return true;
    }

    // Корекція висоти (ToF / Baro)
    void updateAltitude(float z_meas, float r_cov) noexcept {
        const float y = z_meas - x_[2];
        const float S = P_[2] + r_cov;
        const float K = P_[2] / S;

        x_[2] += K * y;
        x_[5] += (K * 0.5f) * y;
        P_[2] *= (1.0f - K);
    }

    // Zero Velocity Update (ZUPT)
    void updateZupt(float r_zupt = 0.001f) noexcept {
        for (size_t i = 3; i < 6; ++i) {
            const float y = 0.0f - x_[i];
            const float S = P_[i] + r_zupt;
            const float K = P_[i] / S;

            x_[i] += K * y;
            P_[i] *= (1.0f - K);

            const size_t b_idx = 6 + (i - 3);
            x_[b_idx] += (P_[b_idx] / S) * y;
        }
    }

    [[nodiscard]] State getState() const noexcept {
        return State{
            .px = x_[0], .py = x_[1], .pz = x_[2],
            .vx = x_[3], .vy = x_[4], .vz = x_[5],
            .bax = x_[6], .bay = x_[7], .baz = x_[8]
        };
    }

private:
    std::array<float, kStateDim> x_{};
    std::array<float, kStateDim> P_{}; // Діагональний вектор дисперсій

    float q_pos_{0.001f};
    float q_vel_{0.05f};
    float q_bias_{0.00001f};
};
