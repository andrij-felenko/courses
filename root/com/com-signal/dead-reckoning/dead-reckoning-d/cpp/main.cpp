#include <cmath>
#include <array>

namespace nav {

constexpr float G_MSS = 9.80665f;

struct Vector3 {
    float x{0.0f}, y{0.0f}, z{0.0f};

    constexpr Vector3 operator+(const Vector3& o) const noexcept { return {x + o.x, y + o.y, z + o.z}; }
    constexpr Vector3 operator-(const Vector3& o) const noexcept { return {x - o.x, y - o.y, z - o.z}; }
    constexpr Vector3 operator*(float s) const noexcept { return {x * s, y * s, z * s}; }
    [[nodiscard]] float norm() const noexcept { return std::sqrt(x * x + y * y + z * z); }
};

struct Quaternion {
    float w{1.0f}, x{0.0f}, y{0.0f}, z{0.0f};

    [[nodiscard]] Quaternion normalized() const noexcept {
        const float n = std::sqrt(w * w + x * x + y * y + z * z);
        return (n < 1e-8f) ? Quaternion{1.0f, 0.0f, 0.0f, 0.0f} : Quaternion{w / n, x / n, y / n, z / n};
    }

    [[nodiscard]] constexpr Quaternion operator*(const Quaternion& b) const noexcept {
        return {
            w * b.w - x * b.x - y * b.y - z * b.z,
            w * b.x + x * b.w + y * b.z - z * b.y,
            w * b.y - x * b.z + y * b.w + z * b.x,
            w * b.z + x * b.y - y * b.x + z * b.w
        };
    }
};

class InsEngine {
public:
    void step(const Vector3& acc_b, const Vector3& gyro_b, float dt) noexcept {
        /* 1. Оновлення кватерніона орієнтації */
        const Vector3 d_th = gyro_b * dt;
        const float th_len = d_th.norm();

        Quaternion dq;
        if (th_len > 1e-7f) {
            const float half = 0.5f * th_len;
            const float s = std::sin(half) / th_len;
            dq = {std::cos(half), d_th.x * s, d_th.y * s, d_th.z * s};
        } else {
            dq = {1.0f, 0.5f * d_th.x, 0.5f * d_th.y, 0.5f * d_th.z};
        }
        q_ = (q_ * dq).normalized();

        /* 2. Поворот питомої сили в навігаційну систему NED */
        const float qw = q_.w, qx = q_.x, qy = q_.y, qz = q_.z;
        const Vector3 f_nav{
            (1.0f - 2.0f * (qy * qy + qz * qz)) * acc_b.x + 2.0f * (qx * qy - qw * qz) * acc_b.y + 2.0f * (qx * qz + qw * qy) * acc_b.z,
            2.0f * (qx * qy + qw * qz) * acc_b.x + (1.0f - 2.0f * (qx * qx + qz * qz)) * acc_b.y + 2.0f * (qy * qz - qw * qx) * acc_b.z,
            2.0f * (qx * qz - qw * qy) * acc_b.x + 2.0f * (qy * qz + qw * qx) * acc_b.y + (1.0f - 2.0f * (qx * qx + qy * qy)) * acc_b.z
        };

        /* 3. Компенсація сили тяжіння */
        const Vector3 cur_acc = f_nav + Vector3{0.0f, 0.0f, G_MSS};

        /* 4. Трапецеїдальне інтегрування швидкості та координат */
        const Vector3 next_vel = vel_ + (prev_acc_ + cur_acc) * (0.5f * dt);
        pos_ = pos_ + (vel_ + next_vel) * (0.5f * dt);

        vel_ = next_vel;
        prev_acc_ = cur_acc;
    }

    [[nodiscard]] const Vector3& position() const noexcept { return pos_; }
    [[nodiscard]] const Vector3& velocity() const noexcept { return vel_; }
    [[nodiscard]] const Quaternion& orientation() const noexcept { return q_; }

private:
    Vector3 pos_{0.0f, 0.0f, 0.0f};
    Vector3 vel_{0.0f, 0.0f, 0.0f};
    Quaternion q_{1.0f, 0.0f, 0.0f, 0.0f};
    Vector3 prev_acc_{0.0f, 0.0f, 0.0f};
};

} // namespace nav
