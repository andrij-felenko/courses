#include <array>
#include <span>
#include <cmath>
#include <cstdint>

class EkfNavigator {
public:
    static constexpr size_t kStateDim = 9;
    static constexpr float kGravity = 9.81f;

    struct State {
        float px, py, pz;
        float vx, vy, vz;
        float bax, bay, baz;
    };

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

        for (size_t i = 0; i < 3; ++i) {
            P_[i]     += (2.0f * P_[3 + i] * dt + q_pos_) * dt;
            P_[3 + i] += q_vel_ * dt;
            P_[6 + i] += q_bias_ * dt;
        }
    }

    // Корекція швидкості оптичним потоком
    [[nodiscard]] bool updateOpticalFlow(float vx_m, float vy_m, float r_flow, float gate_limit = 4.0f) noexcept {
        const std::array<float, 2> z{vx_m, vy_m};

        for (size_t axis = 0; axis < 2; ++axis) {
            const size_t v_idx = 3 + axis;
            const float y = z[axis] - x_[v_idx];
            const float S = P_[v_idx] + r_flow;

            if ((y * y) / S > gate_limit) {
                return false;
            }

            const float K = P_[v_idx] / S;
            x_[v_idx] += K * y;

            const size_t b_idx = 6 + axis;
            x_[b_idx] -= (P_[b_idx] / S) * (y * 0.1f);

            P_[v_idx] *= (1.0f - K);
        }
        return true;
    }

    [[nodiscard]] State getState() const noexcept {
        return State{x_[0], x_[1], x_[2], x_[3], x_[4], x_[5], x_[6], x_[7], x_[8]};
    }

private:
    std::array<float, kStateDim> x_{};
    std::array<float, kStateDim> P_{1.0f, 1.0f, 1.0f, 0.01f, 0.01f, 0.01f, 0.0025f, 0.0025f, 0.0025f};

    float q_pos_{0.001f};
    float q_vel_{0.05f};
    float q_bias_{0.00001f};
};
