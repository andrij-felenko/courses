#include <array>
#include <cmath>
#include <cstdint>
#include <span>

struct Vector3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr Vector3 operator+(const Vector3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vector3 operator-(const Vector3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    [[nodiscard]] constexpr Vector3 operator*(float s) const noexcept {
        return {x * s, y * s, z * s};
    }
};

struct Quaternion {
    float w{1.0f};
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] Vector3 rotate(const Vector3& v) const noexcept {
        const float t2 = w * x; const float t3 = w * y; const float t4 = w * z;
        const float t5 = -x * x; const float t6 = x * y; const float t7 = x * z;
        const float t8 = -y * y; const float t9 = y * z; const float t10 = -z * z;

        return {
            2.0f * ((t8 + t10) * v.x + (t6 - t4) * v.y + (t3 + t7) * v.z) + v.x,
            2.0f * ((t4 + t6) * v.x + (t5 + t10) * v.y + (t9 - t2) * v.z) + v.y,
            2.0f * ((t7 - t3) * v.x + (t2 + t9) * v.y + (t5 + t8) * v.z) + v.z
        };
    }

    void normalize() noexcept {
        const float norm = std::sqrt(w * w + x * x + y * y + z * z);
        if (norm > 1e-6f) {
            const float inv = 1.0f / norm;
            w *= inv; x *= inv; y *= inv; z *= inv;
        }
    }
};

class NavigationEkf {
public:
    struct State {
        Vector3 pos{};
        Vector3 vel{};
        Quaternion q{};
        Vector3 gyro_bias{};
        Vector3 accel_bias{};
        std::array<float, 15> P{};
    };

    NavigationEkf() noexcept {
        state_.P.fill(0.01f);
        state_.P[0] = state_.P[1] = state_.P[2] = 1.0f;       // Позиція: 1 м²
        state_.P[3] = state_.P[4] = state_.P[5] = 0.1f;      // Швидкість: 0.1 (м/с)²
        state_.P[6] = state_.P[7] = state_.P[8] = 0.001f;    // Орієнтація: 0.001 рад²
        state_.P[9] = state_.P[10] = state_.P[11] = 0.01f;   // Bias акселерометра
        state_.P[12] = state_.P[13] = state_.P[14] = 0.0001f;// Bias гіроскопа
    }

    void predict(const Vector3& accel_raw, const Vector3& gyro_raw, float dt) noexcept {
        constexpr float GravityMss = 9.80665f;

        const Vector3 unbias_gyro = gyro_raw - state_.gyro_bias;
        const Vector3 unbias_accel = accel_raw - state_.accel_bias;

        // Інтегрування орієнтації
        const Quaternion dq{1.0f, 0.5f * unbias_gyro.x * dt, 0.5f * unbias_gyro.y * dt, 0.5f * unbias_gyro.z * dt};
        state_.q = Quaternion{
            state_.q.w * dq.w - state_.q.x * dq.x - state_.q.y * dq.y - state_.q.z * dq.z,
            state_.q.w * dq.x + state_.q.x * dq.w + state_.q.y * dq.z - state_.q.z * dq.y,
            state_.q.w * dq.y - state_.q.x * dq.z + state_.q.y * dq.w + state_.q.z * dq.x,
            state_.q.w * dq.z + state_.q.x * dq.y - state_.q.y * dq.x + state_.q.z * dq.w
        };
        state_.q.normalize();

        // Трансформація прискорення в NED та інтегрування швидкості й позиції
        Vector3 acc_ned = state_.q.rotate(unbias_accel);
        acc_ned.z += GravityMss;

        state_.pos = state_.pos + state_.vel * dt + acc_ned * (0.5f * dt * dt);
        state_.vel = state_.vel + acc_ned * dt;

        // Поширення коваріацій
        constexpr float AccelNoiseVar = 0.04f;
        constexpr float GyroNoiseVar = 0.0001f;
        constexpr float AccelBiasVar = 1e-6f;
        constexpr float GyroBiasVar = 1e-8f;

        for (size_t i = 0; i < 3; ++i) {
            state_.P[i] += state_.P[i + 3] * dt + 0.25f * AccelNoiseVar * dt * dt;
            state_.P[i + 3] += AccelNoiseVar * dt;
            state_.P[i + 6] += GyroNoiseVar * dt;
            state_.P[i + 9] += AccelBiasVar * dt;
            state_.P[i + 12] += GyroBiasVar * dt;
        }
    }

    void update_gnss(const Vector3& gnss_pos, const Vector3& gnss_vel, float pos_var, float vel_var) noexcept {
        update_axis(state_.pos.x, gnss_pos.x, state_.P[0], pos_var);
        update_axis(state_.pos.y, gnss_pos.y, state_.P[1], pos_var);
        update_axis(state_.pos.z, gnss_pos.z, state_.P[2], pos_var);

        update_velocity_and_bias(state_.vel.x, state_.accel_bias.x, gnss_vel.x, state_.P[3], state_.P[9], vel_var);
        update_velocity_and_bias(state_.vel.y, state_.accel_bias.y, gnss_vel.y, state_.P[4], state_.P[10], vel_var);
        update_velocity_and_bias(state_.vel.z, state_.accel_bias.z, gnss_vel.z, state_.P[5], state_.P[11], vel_var);
    }

    [[nodiscard]] const State& state() const noexcept { return state_; }

private:
    static void update_axis(float& est, float meas, float& p_var, float r_var) noexcept {
        const float innov = meas - est;
        const float S = p_var + r_var;
        const float K = p_var / S;
        est += K * innov;
        p_var *= (1.0f - K);
    }

    static void update_velocity_and_bias(float& v_est, float& ba_est, float v_meas, float& pv_var, float& pba_var, float r_var) noexcept {
        const float innov = v_meas - v_est;
        const float S = pv_var + r_var;
        const float Kv = pv_var / S;
        v_est += Kv * innov;
        pv_var *= (1.0f - Kv);

        const float Kba = 0.05f * (pba_var / S);
        ba_est -= Kba * innov;
        pba_var *= (1.0f - Kba);
    }

    State state_{};
};
