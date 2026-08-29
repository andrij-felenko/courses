#include "rotation.hpp"

#include <algorithm>

namespace nav {

Quaternion Quaternion::from_axis_angle(const Vector3& axis, float angle_rad) noexcept {
    const auto unit = axis.normalized();
    if (!unit || !std::isfinite(angle_rad)) return {};
    const float half = 0.5F * angle_rad;
    const float s = std::sin(half);
    return {std::cos(half), unit->x * s, unit->y * s, unit->z * s};
}

Quaternion Quaternion::from_rotation_vector(const Vector3& phi) noexcept {
    if (!phi.finite()) return {};
    const float theta = phi.norm();
    if (theta < 1e-7F) {
        // Малий поворот: sin(θ/2)/θ → 1/2, тригонометрія зайва.
        return Quaternion{1.0F, 0.5F * phi.x, 0.5F * phi.y, 0.5F * phi.z}.normalized_fast();
    }
    const float half = 0.5F * theta;
    const float k = std::sin(half) / theta;
    return {std::cos(half), phi.x * k, phi.y * k, phi.z * k};
}

Quaternion Quaternion::from_euler(const EulerAngles& e) noexcept {
    const float cr = std::cos(0.5F * e.roll),  sr = std::sin(0.5F * e.roll);
    const float cp = std::cos(0.5F * e.pitch), sp = std::sin(0.5F * e.pitch);
    const float cy = std::cos(0.5F * e.yaw),   sy = std::sin(0.5F * e.yaw);
    return {cy * cp * cr + sy * sp * sr,
            cy * cp * sr - sy * sp * cr,
            cy * sp * cr + sy * cp * sr,
            sy * cp * cr - cy * sp * sr};
}

Quaternion Quaternion::operator*(const Quaternion& q) const noexcept {
    return {w * q.w - x * q.x - y * q.y - z * q.z,
            w * q.x + x * q.w + y * q.z - z * q.y,
            w * q.y - x * q.z + y * q.w + z * q.x,
            w * q.z + x * q.y - y * q.x + z * q.w};
}

float Quaternion::norm() const noexcept {
    return std::sqrt(w * w + x * x + y * y + z * z);
}

bool Quaternion::finite() const noexcept {
    return std::isfinite(w) && std::isfinite(x) && std::isfinite(y) && std::isfinite(z);
}

Quaternion Quaternion::normalized() const noexcept {
    const float n = norm();
    if (!std::isfinite(n) || n < 1e-9F) return {};   // стан загублено — повертаємось до одиничного
    const float k = 1.0F / n;
    return {w * k, x * k, y * k, z * k};
}

Quaternion Quaternion::normalized_fast() const noexcept {
    const float sq = w * w + x * x + y * y + z * z;
    if (!std::isfinite(sq)) return {};
    // Ряд Тейлора чесний лише поблизу одиниці; далі дешевше заплатити за корінь.
    if (std::fabs(sq - 1.0F) > 2e-2F) return normalized();
    const float k = 1.5F - 0.5F * sq;
    return {w * k, x * k, y * k, z * k};
}

Vector3 Quaternion::rotate(const Vector3& v) const noexcept {
    // v' = v + 2·q_vec × (q_vec × v + w·v): 15 множень і жодної тригонометрії.
    const Vector3 qv{x, y, z};
    const Vector3 t = qv.cross(v) + v * w;
    return v + qv.cross(t) * 2.0F;
}

Vector3 Quaternion::rotate_inverse(const Vector3& v) const noexcept {
    return conjugate().rotate(v);
}

Quaternion Quaternion::integrate_gyro(const Vector3& omega, float dt) const noexcept {
    if (!finite() || !omega.finite() || !std::isfinite(dt)) return {};
    const float h = 0.5F * dt;
    return Quaternion{w + h * (-x * omega.x - y * omega.y - z * omega.z),
                      x + h * ( w * omega.x + y * omega.z - z * omega.y),
                      y + h * ( w * omega.y - x * omega.z + z * omega.x),
                      z + h * ( w * omega.z + x * omega.y - y * omega.x)}
        .normalized_fast();
}

Matrix3 Quaternion::to_matrix() const noexcept {
    const Quaternion n = normalized();
    const float qw = n.w, qx = n.x, qy = n.y, qz = n.z;
    return Matrix3{{{{1.0F - 2.0F * (qy * qy + qz * qz), 2.0F * (qx * qy - qw * qz), 2.0F * (qx * qz + qw * qy)},
                     {2.0F * (qx * qy + qw * qz), 1.0F - 2.0F * (qx * qx + qz * qz), 2.0F * (qy * qz - qw * qx)},
                     {2.0F * (qx * qz - qw * qy), 2.0F * (qy * qz + qw * qx), 1.0F - 2.0F * (qx * qx + qy * qy)}}}};
}

EulerAngles Quaternion::to_euler() const noexcept {
    const Quaternion n = normalized();
    EulerAngles e{};
    e.roll = std::atan2(2.0F * (n.w * n.x + n.y * n.z),
                        1.0F - 2.0F * (n.x * n.x + n.y * n.y));
    // Затиск рятує asin від NaN на похибці округлення float.
    const float sinp = std::clamp(2.0F * (n.w * n.y - n.z * n.x), -1.0F, 1.0F);
    e.pitch = std::asin(sinp);
    e.yaw = std::atan2(2.0F * (n.w * n.z + n.x * n.y),
                       1.0F - 2.0F * (n.y * n.y + n.z * n.z));
    return e;
}

Quaternion nlerp(Quaternion a, Quaternion b, float t) noexcept {
    if (a.w * b.w + a.x * b.x + a.y * b.y + a.z * b.z < 0.0F) {
        b = {-b.w, -b.x, -b.y, -b.z};   // найкоротший шлях по гіперсфері
    }
    const float u = 1.0F - t;
    return Quaternion{u * a.w + t * b.w, u * a.x + t * b.x,
                      u * a.y + t * b.y, u * a.z + t * b.z}
        .normalized();
}

Quaternion slerp(Quaternion a, Quaternion b, float t) noexcept {
    a = a.normalized();
    b = b.normalized();
    float d = a.w * b.w + a.x * b.x + a.y * b.y + a.z * b.z;
    if (d < 0.0F) {
        b = {-b.w, -b.x, -b.y, -b.z};
        d = -d;
    }
    if (d > 0.9995F) return nlerp(a, b, t);   // дуга майже пряма: sin(Ω) прямує до нуля
    const float omega = std::acos(std::clamp(d, -1.0F, 1.0F));
    const float s = std::sin(omega);
    const float k0 = std::sin((1.0F - t) * omega) / s;
    const float k1 = std::sin(t * omega) / s;
    return Quaternion{k0 * a.w + k1 * b.w, k0 * a.x + k1 * b.x,
                      k0 * a.y + k1 * b.y, k0 * a.z + k1 * b.z}
        .normalized();
}

std::expected<EulerAngles, KinematicError> euler_rates(const EulerAngles& angles,
                                                       const Vector3& omega) noexcept {
    if (!omega.finite() || !std::isfinite(angles.pitch) || !std::isfinite(angles.roll)) {
        return std::unexpected(KinematicError::BadInput);
    }
    const float ct = std::cos(angles.pitch);
    if (std::fabs(ct) < 1e-3F) return std::unexpected(KinematicError::GimbalLock);
    const float sr = std::sin(angles.roll);
    const float cr = std::cos(angles.roll);
    const float common = omega.y * sr + omega.z * cr;
    return EulerAngles{omega.x + common * (std::sin(angles.pitch) / ct),
                       omega.y * cr - omega.z * sr,
                       common / ct};
}

}  // namespace nav
