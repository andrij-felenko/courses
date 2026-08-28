#include <cstdint>
#include <cmath>
#include <algorithm>
#include <numbers>

// 3D Вектор із перевантаженими операторами
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
    constexpr Vec3& operator+=(const Vec3& o) noexcept {
        x += o.x; y += o.y; z += o.z;
        return *this;
    }
    [[nodiscard]] constexpr Vec3 cross(const Vec3& o) const noexcept {
        return { y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x };
    }
};

// Кути Ейлера (радіани)
struct Euler {
    float roll{0.0f};
    float pitch{0.0f};
    float yaw{0.0f};
};

// Одиничний кватерніон Гамільтона
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

    // Інтегрування методом Рунге-Кутти 2-го порядку (RK2)
    [[nodiscard]] Quat integrate_rk2(const Vec3& omega, float dt) const noexcept {
        const float h = 0.5f * dt;

        // k1
        const Quat k1{
            0.5f * (-x * omega.x - y * omega.y - z * omega.z),
            0.5f * ( w * omega.x + y * omega.z - z * omega.y),
            0.5f * ( w * omega.y - x * omega.z + z * omega.x),
            0.5f * ( w * omega.z + x * omega.y - y * omega.x)
        };

        const Quat q_mid = Quat{ w + k1.w * h, x + k1.x * h, y + k1.y * h, z + k1.z * h }.normalized();

        // k2
        const Quat k2{
            0.5f * (-q_mid.x * omega.x - q_mid.y * omega.y - q_mid.z * omega.z),
            0.5f * ( q_mid.w * omega.x + q_mid.y * omega.z - q_mid.z * omega.y),
            0.5f * ( q_mid.w * omega.y - q_mid.x * omega.z + q_mid.z * omega.x),
            0.5f * ( q_mid.w * omega.z + q_mid.x * omega.y - q_mid.y * omega.x)
        };

        return Quat{ w + k2.w * dt, x + k2.x * dt, y + k2.y * dt, z + k2.z * dt }.normalized();
    }

    // Поворот вектора з Body у NED за формулою Родрігеса
    [[nodiscard]] Vec3 rotate_to_ned(const Vec3& v) const noexcept {
        const Vec3 q_vec{ x, y, z };
        const Vec3 t = q_vec.cross(v) * 2.0f;
        return v + t * w + q_vec.cross(t);
    }

    // Безпечне видобування кутів Ейлера із захистом від NaN
    [[nodiscard]] Euler to_euler() const noexcept {
        const float roll = std::atan2(2.0f * (w * x + y * z), 1.0f - 2.0f * (x * x + y * y));
        const float sin_pitch = std::clamp(2.0f * (w * y - z * x), -1.0f, 1.0f);
        const float pitch = std::asin(sin_pitch);
        const float yaw = std::atan2(2.0f * (w * z + x * y), 1.0f - 2.0f * (y * y + z * z));
        return { roll, pitch, yaw };
    }
};

// Стан апарата
struct VehicleState {
    Vec3  position_ned{};
    Vec3  velocity_ned{};
    Quat  attitude{};
    Vec3  angular_rate_b{};
    Vec3  linear_accel_b{};
    Vec3  gyro_bias_b{};
    Vec3  accel_bias_b{};

    void update_imu(const Vec3& gyro_raw, const Vec3& accel_raw, float dt) noexcept {
        if (dt <= 0.0f) return;

        angular_rate_b = gyro_raw - gyro_bias_b;
        const Vec3 accel_corr = accel_raw - accel_bias_b;
        linear_accel_b = accel_corr;

        // 1. Оновлення орієнтації
        attitude = attitude.integrate_rk2(angular_rate_b, dt);

        // 2. Обертання прискорення та компенсація тяжіння
        Vec3 accel_ned = attitude.rotate_to_ned(accel_corr);
        accel_ned.z += 9.80665f;

        // 3. Інтегрування швидкості та позиції
        velocity_ned += accel_ned * dt;
        position_ned += velocity_ned * dt;
    }
};
