#include <iostream>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <algorithm>

struct Quaternion {
    double w{1.0};
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] double dot(const Quaternion& other) const noexcept {
        return w * other.w + x * other.x + y * other.y + z * other.z;
    }

    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(w * w + x * x + y * y + z * z);
    }

    [[nodiscard]] Quaternion normalized() const noexcept {
        const double mag = norm();
        if (mag < 1e-12) {
            return Quaternion{1.0, 0.0, 0.0, 0.0};
        }
        return Quaternion{w / mag, x / mag, y / mag, z / mag};
    }

    [[nodiscard]] static Quaternion slerp(const Quaternion& q1, Quaternion q2, double t) noexcept {
        double cos_omega = q1.dot(q2);

        // Якщо скалярний добуток від'ємний, інвертуємо цільовий кватерніон
        // для вибору найкоротшої геодезичної дуги (< 180 градусів)
        if (cos_omega < 0.0) {
            cos_omega = -cos_omega;
            q2.w = -q2.w;
            q2.x = -q2.x;
            q2.y = -q2.y;
            q2.z = -q2.z;
        }

        cos_omega = std::clamp(cos_omega, -1.0, 1.0);

        // Область близькості: заміна на NLERP заради числової стабільності
        if (cos_omega > 0.9995) {
            Quaternion res{
                q1.w + t * (q2.w - q1.w),
                q1.x + t * (q2.x - q1.x),
                q1.y + t * (q2.y - q1.y),
                q1.z + t * (q2.z - q1.z)
            };
            return res.normalized();
        }

        const double omega = std::acos(cos_omega);
        const double sin_omega = std::sin(omega);
        const double scale1 = std::sin((1.0 - t) * omega) / sin_omega;
        const double scale2 = std::sin(t * omega) / sin_omega;

        return Quaternion{
            scale1 * q1.w + scale2 * q2.w,
            scale1 * q1.x + scale2 * q2.x,
            scale1 * q1.y + scale2 * q2.y,
            scale1 * q1.z + scale2 * q2.z
        };
    }
};

int main() {
    // Поворот від 0° до 90° навколо осі Z
    const Quaternion q_start{1.0, 0.0, 0.0, 0.0};
    const double angle = std::numbers::pi / 4.0;
    const Quaternion q_end{std::cos(angle), 0.0, 0.0, std::sin(angle)};

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Інтерполяція орієнтації C++:\n";

    for (int step = 0; step <= 4; ++step) {
        const double t = step * 0.25;
        const Quaternion q_interp = Quaternion::slerp(q_start, q_end, t);
        std::cout << "t = " << t << " -> (w: " << q_interp.w
                  << ", x: " << q_interp.x
                  << ", y: " << q_interp.y
                  << ", z: " << q_interp.z << ")\n";
    }
    return 0;
}
