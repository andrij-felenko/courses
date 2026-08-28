#include <iostream>
#include <cmath>
#include <array>
#include <optional>

namespace nav {

constexpr float GRAVITY_MSS = 9.80665f;

struct Vector3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    constexpr Vector3 operator+(const Vector3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    constexpr Vector3 operator-(const Vector3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    constexpr Vector3 operator*(float s) const noexcept {
        return {x * s, y * s, z * s};
    }
    [[nodiscard]] float norm() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }
};

struct Quaternion {
    float w{1.0f};
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] Quaternion normalized() const noexcept {
        const float n = std::sqrt(w * w + x * x + y * y + z * z);
        if (n < 1e-8f) return {1.0f, 0.0f, 0.0f, 0.0f};
        const float inv = 1.0f / n;
        return {w * inv, x * inv, y * inv, z * inv};
    }

    [[nodiscard]] constexpr Quaternion operator*(const Quaternion& b) const noexcept {
        return {
            w * b.w - x * b.x - y * b.y - z * b.z,
            w * b.x + x * b.w + y * b.z - z * b.y,
            w * b.y - x * b.z + y * b.w + z * b.x,
            w * b.z + x * b.y - y * b.x + z * b.w
        };
    }

    [[nodiscard]] std::array<std::array<float, 3>, 3> to_rotation_matrix() const noexcept {
        const float qx2 = x * x, qy2 = y * y, qz2 = z * z;
        return {{
            {1.0f - 2.0f * (qy2 + qz2), 2.0f * (x * y - w * z), 2.0f * (x * z + w * y)},
            {2.0f * (x * y + w * z), 1.0f - 2.0f * (qx2 + qz2), 2.0f * (y * z - w * x)},
            {2.0f * (x * z - w * y), 2.0f * (y * z + w * x), 1.0f - 2.0f * (qx2 + qy2)}
        }};
    }
};

class StrapdownIns {
public:
    struct ImuSample {
        Vector3 accel_ms2;  /* Сира питома сила корпусу [м/с²] */
        Vector3 gyro_rads;   /* Сира кутова швидкість корпусу [рад/с] */
        float dt_sec{0.01f}; /* Інтервал дискретизації */
    };

    struct Calibration {
        Vector3 accel_bias{0.0f, 0.0f, 0.0f};
        Vector3 gyro_bias{0.0f, 0.0f, 0.0f};
    };

    explicit StrapdownIns(Vector3 init_pos = {}, Vector3 init_vel = {}, Quaternion init_q = {}) noexcept
        : pos_{init_pos}, vel_{init_vel}, q_{init_q.normalized()} {}

    void set_calibration(const Calibration& calib) noexcept {
        calib_ = calib;
    }

    void update(const ImuSample& imu) noexcept {
        /* 1. Компенсація зміщень нуля давачів */
        const Vector3 unb_gyro = imu.gyro_rads - calib_.gyro_bias;
        const Vector3 unb_acc  = imu.accel_ms2 - calib_.accel_bias;

        /* 2. Інтегрування кватерніона орієнтації */
        const Vector3 d_theta = unb_gyro * imu.dt_sec;
        const float angle = d_theta.norm();

        Quaternion dq;
        if (angle > 1e-8f) {
            const float half_angle = 0.5f * angle;
            const float factor = std::sin(half_angle) / angle;
            dq = {std::cos(half_angle), d_theta.x * factor, d_theta.y * factor, d_theta.z * factor};
        } else {
            dq = {1.0f, 0.5f * d_theta.x, 0.5f * d_theta.y, 0.5f * d_theta.z};
        }
        q_ = (q_ * dq).normalized();

        /* 3. Поворот прискорення у навігаційну систему NED */
        const auto r = q_.to_rotation_matrix();
        const Vector3 f_nav{
            r[0][0] * unb_acc.x + r[0][1] * unb_acc.y + r[0][2] * unb_acc.z,
            r[1][0] * unb_acc.x + r[1][1] * unb_acc.y + r[1][2] * unb_acc.z,
            r[2][0] * unb_acc.x + r[2][1] * unb_acc.y + r[2][2] * unb_acc.z
        };

        /* 4. Компенсація сили тяжіння */
        const Vector3 cur_acc = f_nav + Vector3{0.0f, 0.0f, GRAVITY_MSS};

        /* 5. Трапецеїдальне чисельне інтегрування швидкості та координат */
        const Vector3 avg_acc = (prev_acc_ + cur_acc) * 0.5f;
        const Vector3 next_vel = vel_ + avg_acc * imu.dt_sec;
        const Vector3 avg_vel = (vel_ + next_vel) * 0.5f;

        pos_ = pos_ + avg_vel * imu.dt_sec;
        vel_ = next_vel;
        prev_acc_ = cur_acc;
    }

    bool check_and_apply_zupt(const Vector3& raw_acc, const Vector3& raw_gyro,
                              float gyro_thresh = 0.05f, float acc_thresh = 0.2f) noexcept {
        const float g_diff = std::abs(raw_acc.norm() - GRAVITY_MSS);
        const float w_norm = raw_gyro.norm();

        if (g_diff < acc_thresh && w_norm < gyro_thresh) {
            vel_ = {0.0f, 0.0f, 0.0f};
            prev_acc_ = {0.0f, 0.0f, 0.0f};
            return true;
        }
        return false;
    }

    [[nodiscard]] const Vector3& position() const noexcept { return pos_; }
    [[nodiscard]] const Vector3& velocity() const noexcept { return vel_; }
    [[nodiscard]] const Quaternion& orientation() const noexcept { return q_; }

private:
    Vector3 pos_{0.0f, 0.0f, 0.0f};
    Vector3 vel_{0.0f, 0.0f, 0.0f};
    Quaternion q_{1.0f, 0.0f, 0.0f, 0.0f};
    Vector3 prev_acc_{0.0f, 0.0f, 0.0f};
    Calibration calib_{};
};

} // namespace nav

int main() {
    nav::StrapdownIns ins;
    constexpr float dt = 0.01f;

    std::cout << "=== Тест StrapdownIns C++ (100 Гц) ===\n";

    /* Симуляція розгону 2.0 м/с² по осі North протягом 2 с */
    for (int i = 0; i < 200; ++i) {
        ins.update({{2.0f, 0.0f, -nav::GRAVITY_MSS}, {0.0f, 0.0f, 0.0f}, dt});
    }

    const auto p1 = ins.position();
    const auto v1 = ins.velocity();
    std::cout << "Після 2 с розгону: Pos=(" << p1.x << ", " << p1.y << ", " << p1.z
              << ") м, Vel=(" << v1.x << ", " << v1.y << ", " << v1.z << ") м/с\n";

    /* Симуляція рівномірного руху протягом 3 с */
    for (int i = 0; i < 300; ++i) {
        ins.update({{0.0f, 0.0f, -nav::GRAVITY_MSS}, {0.0f, 0.0f, 0.0f}, dt});
    }

    const auto p2 = ins.position();
    const auto v2 = ins.velocity();
    std::cout << "Після 3 с круїзу: Pos=(" << p2.x << ", " << p2.y << ", " << p2.z
              << ") м, Vel=(" << v2.x << ", " << v2.y << ", " << v2.z << ") м/с\n";

    return 0;
}
