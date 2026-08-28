/* Ідіоматична реалізація орієнтаційного фільтра IMU на C++20 */
#include <array>
#include <cmath>
#include <algorithm>

namespace Navigation {

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

class AttitudeObserver {
public:
    struct Config {
        float kp{1.2f};
        float ki{0.05f};
        float minGravityGate{0.85f};
        float maxGravityGate{1.15f};
    };

    explicit constexpr AttitudeObserver(Config config = {}) noexcept
        : cfg_{config} {}

    void update(const std::array<float, 3>& gyroRadSec,
                const std::array<float, 3>& accelUnits,
                float dt) noexcept {
        float gx = gyroRadSec[0];
        float gy = gyroRadSec[1];
        float gz = gyroRadSec[2];

        float ax = accelUnits[0];
        float ay = accelUnits[1];
        float az = accelUnits[2];

        float ex = 0.0f;
        float ey = 0.0f;
        float ez = 0.0f;

        const float aNormSq = ax * ax + ay * ay + az * az;
        if (aNormSq > 0.001f) {
            const float invNorm = 1.0f / std::sqrt(aNormSq);
            ax *= invNorm;
            ay *= invNorm;
            az *= invNorm;

            const float aMagnitude = 1.0f / invNorm;
            if (aMagnitude >= cfg_.minGravityGate && aMagnitude <= cfg_.maxGravityGate) {
                const float vx = 2.0f * (q_.x * q_.z - q_.w * q_.y);
                const float vy = 2.0f * (q_.w * q_.x + q_.y * q_.z);
                const float vz = q_.w * q_.w - q_.x * q_.x - q_.y * q_.y + q_.z * q_.z;

                ex = (ay * vz - az * vy);
                ey = (az * vx - ax * vz);
                ez = (ax * vy - ay * vx);

                if (cfg_.ki > 0.0f) {
                    gyroBias_[0] -= cfg_.ki * ex * dt;
                    gyroBias_[1] -= cfg_.ki * ey * dt;
                    gyroBias_[2] -= cfg_.ki * ez * dt;
                }
            }
        }

        gx = gx - gyroBias_[0] + cfg_.kp * ex;
        gy = gy - gyroBias_[1] + cfg_.kp * ey;
        gz = gz - gyroBias_[2] + cfg_.kp * ez;

        const float halfDt = 0.5f * dt;
        const float qw = q_.w;
        const float qx = q_.x;
        const float qy = q_.y;
        const float qz = q_.z;

        q_.w += halfDt * (-qx * gx - qy * gy - qz * gz);
        q_.x += halfDt * ( qw * gx + qy * gz - qz * gy);
        q_.y += halfDt * ( qw * gy - qx * gz + qz * gx);
        q_.z += halfDt * ( qw * gz + qx * gy - qy * gx);

        q_.normalize();
    }

    [[nodiscard]] const Quaternion& orientation() const noexcept { return q_; }
    [[nodiscard]] const std::array<float, 3>& bias() const noexcept { return gyroBias_; }

private:
    Config cfg_{};
    Quaternion q_{};
    std::array<float, 3> gyroBias_{0.0f, 0.0f, 0.0f};
};

} // namespace Navigation
