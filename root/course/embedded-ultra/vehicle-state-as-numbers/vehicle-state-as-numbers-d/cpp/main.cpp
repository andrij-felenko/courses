#include <cstdint>
#include <cmath>
#include <algorithm>
#include <numbers>

// Тривимірний вектор із векторними операціями
struct Vec3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr Vec3 operator+(const Vec3& o) const noexcept {
        return { x + o.x, y + o.y, z + o.z };
    }
    [[nodiscard]] constexpr Vec3 operator-(const Vec3& o) const noexcept {
        return { x - o.x, y - o.y, z - o.z };
    }
    [[nodiscard]] constexpr Vec3 operator*(float s) const noexcept {
        return { x * s, y * s, z * s };
    }
    [[nodiscard]] constexpr Vec3 cross(const Vec3& o) const noexcept {
        return { y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x };
    }
    [[nodiscard]] constexpr float dot(const Vec3& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }
};

// Одиничний кватерніон просторового обертання
struct Quat {
    float w{1.0f};
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] Quat normalized() const noexcept {
        const float sq = w * w + x * x + y * y + z * z;
        if (sq < 1e-12f) {
            return { 1.0f, 0.0f, 0.0f, 0.0f };
        }
        const float inv = 1.0f / std::sqrt(sq);
        return { w * inv, x * inv, y * inv, z * inv };
    }

    // Чисельне інтегрування орієнтації на кроці dt
    [[nodiscard]] Quat integrate(const Vec3& omega, float dt) const noexcept {
        const float half_dt = 0.5f * dt;
        const Quat dq{
            half_dt * (-x * omega.x - y * omega.y - z * omega.z),
            half_dt * ( w * omega.x + y * omega.z - z * omega.y),
            half_dt * ( w * omega.y - x * omega.z + z * omega.x),
            half_dt * ( w * omega.z + x * omega.y - y * omega.x)
        };
        return Quat{ w + dq.w, x + dq.x, y + dq.y, z + dq.z }.normalized();
    }

    // Поворот вектора з Body у NED без створення проміжних кватерніонів
    [[nodiscard]] Vec3 rotate(const Vec3& v) const noexcept {
        const Vec3 q_vec{ x, y, z };
        const Vec3 t = q_vec.cross(v) * 2.0f;
        return v + t * w + q_vec.cross(t);
    }

    // Перетворення у кути Ейлера (roll, pitch, yaw) у радіанах
    [[nodiscard]] Vec3 to_euler() const noexcept {
        const float roll = std::atan2(2.0f * (w * x + y * z), 1.0f - 2.0f * (x * x + y * y));
        const float sin_pitch = std::clamp(2.0f * (w * y - z * x), -1.0f, 1.0f);
        const float pitch = std::asin(sin_pitch);
        const float yaw = std::atan2(2.0f * (w * z + x * y), 1.0f - 2.0f * (y * y + z * z));
        return { roll, pitch, yaw };
    }
};

// Повний стан апарата
struct VehicleState {
    Vec3  position_ned{};   // координати в метрах
    Vec3  velocity_ned{};   // швидкість у м/с
    Quat  attitude{};       // орієнтація Body -> NED
    Vec3  angular_rate_b{}; // кутові швидкості в рад/с
    Vec3  accel_bias_b{};   // зміщення акселерометра
    Vec3  gyro_bias_b{};    // зміщення гіроскопа
};
