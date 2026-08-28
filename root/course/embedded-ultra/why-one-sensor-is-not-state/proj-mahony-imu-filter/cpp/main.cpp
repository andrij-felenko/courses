#include <array>
#include <cmath>
#include <concepts>
#include <numbers>
#include <algorithm>

struct EulerAngles {
    float roll{};   // Крен (рад)
    float pitch{};  // Тангаж (рад)
    float yaw{};    // Курс (рад)
};

struct Quaternion {
    float w{1.0f};
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr float normSquare() const noexcept {
        return w * w + x * x + y * y + z * z;
    }

    void normalize() noexcept {
        const float invNorm = 1.0f / std::sqrt(normSquare());
        w *= invNorm;
        x *= invNorm;
        y *= invNorm;
        z *= invNorm;
    }
};

class MahonyAttitudeFilter {
public:
    explicit constexpr MahonyAttitudeFilter(float kp = 1.0f, float ki = 0.05f) noexcept
        : twoKp_{2.0f * kp}, twoKi_{2.0f * ki} {}

    void update(const std::array<float, 3>& gyroRadSec,
                const std::array<float, 3>& accelG,
                float dt) noexcept {
        float gx = gyroRadSec[0];
        float gy = gyroRadSec[1];
        float gz = gyroRadSec[2];
        float ax = accelG[0];
        float ay = accelG[1];
        float az = accelG[2];

        const float aNormSq = ax * ax + ay * ay + az * az;
        if (aNormSq > 0.0001f) {
            const float recipNorm = 1.0f / std::sqrt(aNormSq);
            ax *= recipNorm;
            ay *= recipNorm;
            az *= recipNorm;

            const float aMag = 1.0f / recipNorm;
            // Динамічний гейтинг прискорень під час активних перевантажень
            if (aMag >= 0.80f && aMag <= 1.20f) {
                const float halfvx = q_.x * q_.z - q_.w * q_.y;
                const float halfvy = q_.w * q_.x + q_.y * q_.z;
                const float halfvz = q_.w * q_.w - 0.5f + q_.z * q_.z;

                const float halfex = ay * halfvz - az * halfvy;
                const float halfey = az * halfvx - ax * halfvz;
                const float halfez = ax * halfvy - ay * halfvx;

                if (twoKi_ > 0.0f) {
                    integralBias_[0] += twoKi_ * halfex * dt;
                    integralBias_[1] += twoKi_ * halfey * dt;
                    integralBias_[2] += twoKi_ * halfez * dt;
                    gx += integralBias_[0];
                    gy += integralBias_[1];
                    gz += integralBias_[2];
                }

                gx += twoKp_ * halfex;
                gy += twoKp_ * halfey;
                gz += twoKp_ * halfez;
            }
        }

        gx *= (0.5f * dt);
        gy *= (0.5f * dt);
        gz *= (0.5f * dt);

        const float qw = q_.w;
        const float qx = q_.x;
        const float qy = q_.y;
        const float qz = q_.z;

        q_.w += (-qx * gx - qy * gy - qz * gz);
        q_.x += ( qw * gx + qy * gz - qz * gy);
        q_.y += ( qw * gy - qx * gz + qz * gx);
        q_.z += ( qw * gz + qx * gy - qy * gx);

        q_.normalize();
    }

    [[nodiscard]] EulerAngles toEuler() const noexcept {
        return EulerAngles{
            .roll  = std::atan2(2.0f * (q_.w * q_.x + q_.y * q_.z), 1.0f - 2.0f * (q_.x * q_.x + q_.y * q_.y)),
            .pitch = std::asin(std::clamp(2.0f * (q_.w * q_.y - q_.z * q_.x), -1.0f, 1.0f)),
            .yaw   = std::atan2(2.0f * (q_.w * q_.z + q_.x * q_.y), 1.0f - 2.0f * (q_.y * q_.y + q_.z * q_.z))
        };
    }

    [[nodiscard]] const Quaternion& quaternion() const noexcept { return q_; }
    [[nodiscard]] const std::array<float, 3>& gyroBias() const noexcept { return integralBias_; }

private:
    Quaternion q_{};
    std::array<float, 3> integralBias_{0.0f, 0.0f, 0.0f};
    float twoKp_{2.0f};
    float twoKi_{0.1f};
};
