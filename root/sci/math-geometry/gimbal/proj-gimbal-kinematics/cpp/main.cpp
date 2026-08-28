#include <array>
#include <cmath>
#include <numbers>
#include <optional>

namespace gimbal {

constexpr float Pi = std::numbers::pi_v<float>;
constexpr float PitchLimit = 88.0f * Pi / 180.0f;

struct Vec3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr float norm() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }

    [[nodiscard]] Vec3 normalized() const noexcept {
        const float n = norm();
        if (n < 1e-6f) {
            return Vec3{1.0f, 0.0f, 0.0f};
        }
        return Vec3{x / n, y / n, z / n};
    }
};

struct Angles {
    float yaw{0.0f};    // ψ навколо Z, радіани
    float pitch{0.0f};  // θ навколо Y, радіани
    float roll{0.0f};   // φ навколо X, радіани
};

class Mat3 {
public:
    std::array<std::array<float, 3>, 3> data{};

    constexpr Mat3() noexcept = default;

    [[nodiscard]] static Mat3 from_euler(const Angles& a) noexcept {
        const float cy = std::cos(a.yaw),   sy = std::sin(a.yaw);
        const float cp = std::cos(a.pitch), sp = std::sin(a.pitch);
        const float cr = std::cos(a.roll),  sr = std::sin(a.roll);

        Mat3 r;
        r.data[0][0] = cy * cp;
        r.data[0][1] = cy * sp * sr - sy * cr;
        r.data[0][2] = cy * sp * cr + sy * sr;

        r.data[1][0] = sy * cp;
        r.data[1][1] = sy * sp * sr + cy * cr;
        r.data[1][2] = sy * sp * cr - cy * sr;

        r.data[2][0] = -sp;
        r.data[2][1] = cp * sr;
        r.data[2][2] = cp * cr;
        return r;
    }

    [[nodiscard]] Mat3 transpose() const noexcept {
        Mat3 r;
        for (size_t i = 0; i < 3; ++i) {
            for (size_t j = 0; j < 3; ++j) {
                r.data[i][j] = data[j][i];
            }
        }
        return r;
    }

    [[nodiscard]] Angles to_euler() const noexcept {
        Angles out;
        float sp = -data[2][0];
        if (sp > 1.0f) sp = 1.0f;
        if (sp < -1.0f) sp = -1.0f;

        out.pitch = std::asin(sp);

        if (std::abs(out.pitch) > PitchLimit) {
            out.roll = 0.0f;
            out.yaw = std::atan2(-data[0][1], data[1][1]);
            return out;
        }

        out.roll = std::atan2(data[2][1], data[2][2]);
        out.yaw = std::atan2(data[1][0], data[0][0]);
        return out;
    }

    [[nodiscard]] friend Mat3 operator*(const Mat3& a, const Mat3& b) noexcept {
        Mat3 r;
        for (size_t i = 0; i < 3; ++i) {
            for (size_t j = 0; j < 3; ++j) {
                r.data[i][j] = a.data[i][0] * b.data[0][j] +
                               a.data[i][1] * b.data[1][j] +
                               a.data[i][2] * b.data[2][j];
            }
        }
        return r;
    }

    [[nodiscard]] friend Vec3 operator*(const Mat3& m, const Vec3& v) noexcept {
        return Vec3{
            m.data[0][0] * v.x + m.data[0][1] * v.y + m.data[0][2] * v.z,
            m.data[1][0] * v.x + m.data[1][1] * v.y + m.data[1][2] * v.z,
            m.data[2][0] * v.x + m.data[2][1] * v.y + m.data[2][2] * v.z
        };
    }
};

/* Пряма кінематика: розрахунок вектора лінії візування камери у світових координатах */
[[nodiscard]] inline Vec3 forward_kinematics(const Mat3& body_rot, const Angles& gimbal_angles) noexcept {
    const Mat3 gimbal_rot = Mat3::from_euler(gimbal_angles);
    const Mat3 cam_rot = body_rot * gimbal_rot;
    return cam_rot * Vec3{1.0f, 0.0f, 0.0f};
}

/* Зворотна кінематика: розрахунок кутів підвісу для спрямування камери на ціль */
[[nodiscard]] inline Angles inverse_targeting(const Mat3& body_rot, const Vec3& target_world) noexcept {
    const Mat3 body_inv = body_rot.transpose();
    const Vec3 target_norm = target_world.normalized();
    const Vec3 v_body = body_inv * target_norm;

    Angles angles;
    angles.yaw = std::atan2(v_body.y, v_body.x);
    
    const float hyp = std::sqrt(v_body.x * v_body.x + v_body.y * v_body.y);
    angles.pitch = std::atan2(-v_body.z, hyp);
    angles.roll = 0.0f;

    if (angles.pitch > PitchLimit) angles.pitch = PitchLimit;
    if (angles.pitch < -PitchLimit) angles.pitch = -PitchLimit;

    return angles;
}

/* Компенсація збурень корпусу: знаходження кутів підвісу для збереження інерціального положення */
[[nodiscard]] inline Angles stabilize_attitude(const Mat3& body_rot, const Mat3& desired_world_rot) noexcept {
    const Mat3 gimbal_rot = body_rot.transpose() * desired_world_rot;
    return gimbal_rot.to_euler();
}

} // namespace gimbal
