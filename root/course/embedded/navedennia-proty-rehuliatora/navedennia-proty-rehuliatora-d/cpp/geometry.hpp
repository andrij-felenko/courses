#pragma once

// Геометрія бортового стеку: вектор і кватерніон як значення.
// Усе constexpr там, де математика це дозволяє, — компілятор згортає
// сталі уставки й межі ще на етапі трансляції.

#include <algorithm>
#include <cmath>
#include <numbers>

namespace flight {

struct Vec3 {
    float x{0.0F};
    float y{0.0F};
    float z{0.0F};

    constexpr Vec3 operator+(const Vec3& r) const noexcept { return {x + r.x, y + r.y, z + r.z}; }
    constexpr Vec3 operator-(const Vec3& r) const noexcept { return {x - r.x, y - r.y, z - r.z}; }
    constexpr Vec3 operator*(float k) const noexcept { return {x * k, y * k, z * k}; }
    constexpr Vec3 operator-() const noexcept { return {-x, -y, -z}; }

    constexpr Vec3& operator+=(const Vec3& r) noexcept { x += r.x; y += r.y; z += r.z; return *this; }

    [[nodiscard]] constexpr float normSq() const noexcept { return x * x + y * y + z * z; }
    [[nodiscard]] float norm() const noexcept { return std::sqrt(normSq()); }

    // Нормалізація з явним запасним напрямком: нульовий вектор не має напрямку.
    [[nodiscard]] Vec3 normalizedOr(const Vec3& fallback) const noexcept {
        const float n = norm();
        return (n < 1e-6F) ? fallback : *this * (1.0F / n);
    }

    // Обмеження ДОВЖИНИ зі збереженням напрямку — не покомпонентний clamp.
    [[nodiscard]] Vec3 clampedNorm(float maxNorm) const noexcept {
        const float n = norm();
        return (n <= maxNorm || n < 1e-6F) ? *this : *this * (maxNorm / n);
    }
};

[[nodiscard]] constexpr float dot(const Vec3& a, const Vec3& b) noexcept {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

[[nodiscard]] constexpr Vec3 cross(const Vec3& a, const Vec3& b) noexcept {
    return {a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x};
}

[[nodiscard]] inline Vec3 clampAxes(const Vec3& v, const Vec3& lo, const Vec3& hi) noexcept {
    return {std::clamp(v.x, lo.x, hi.x),
            std::clamp(v.y, lo.y, hi.y),
            std::clamp(v.z, lo.z, hi.z)};
}

struct Quat {
    float w{1.0F};
    float x{0.0F};
    float y{0.0F};
    float z{0.0F};

    [[nodiscard]] constexpr Quat conjugate() const noexcept { return {w, -x, -y, -z}; }
    [[nodiscard]] constexpr Vec3 vec() const noexcept { return {x, y, z}; }

    [[nodiscard]] constexpr Quat operator*(const Quat& r) const noexcept {
        return {w * r.w - x * r.x - y * r.y - z * r.z,
                w * r.x + x * r.w + y * r.z - z * r.y,
                w * r.y - x * r.z + y * r.w + z * r.x,
                w * r.z + x * r.y - y * r.x + z * r.w};
    }

    [[nodiscard]] Quat normalized() const noexcept {
        const float n = std::sqrt(w * w + x * x + y * y + z * z);
        if (n < 1e-6F) {
            return Quat{};
        }
        const float k = 1.0F / n;
        return {w * k, x * k, y * k, z * k};
    }

    // Поворот вектора зі зв'язаної системи в навігаційну.
    [[nodiscard]] Vec3 rotate(const Vec3& v) const noexcept {
        const Vec3 t = cross(vec(), v) * 2.0F;
        return v + t * w + cross(vec(), t);
    }

    [[nodiscard]] static Quat fromAxisAngle(const Vec3& axisUnit, float angle) noexcept {
        const float half = angle * 0.5F;
        const float s = std::sin(half);
        return {std::cos(half), axisUnit.x * s, axisUnit.y * s, axisUnit.z * s};
    }

    // Кватерніон з ортонормованого тригранника (стовпці матриці body->NED).
    // Метод Шеппарда: гілка з найбільшим знаменником тримає точність біля 180 гр.
    [[nodiscard]] static Quat fromBasis(const Vec3& xb, const Vec3& yb, const Vec3& zb) noexcept {
        const float r00 = xb.x, r01 = yb.x, r02 = zb.x;
        const float r10 = xb.y, r11 = yb.y, r12 = zb.y;
        const float r20 = xb.z, r21 = yb.z, r22 = zb.z;
        const float trace = r00 + r11 + r22;

        if (trace > 0.0F) {
            const float s = std::sqrt(trace + 1.0F) * 2.0F;
            return Quat{0.25F * s, (r21 - r12) / s, (r02 - r20) / s, (r10 - r01) / s}.normalized();
        }
        if (r00 > r11 && r00 > r22) {
            const float s = std::sqrt(1.0F + r00 - r11 - r22) * 2.0F;
            return Quat{(r21 - r12) / s, 0.25F * s, (r01 + r10) / s, (r02 + r20) / s}.normalized();
        }
        if (r11 > r22) {
            const float s = std::sqrt(1.0F + r11 - r00 - r22) * 2.0F;
            return Quat{(r02 - r20) / s, (r01 + r10) / s, 0.25F * s, (r12 + r21) / s}.normalized();
        }
        const float s = std::sqrt(1.0F + r22 - r00 - r11) * 2.0F;
        return Quat{(r10 - r01) / s, (r02 + r20) / s, (r12 + r21) / s, 0.25F * s}.normalized();
    }
};

// Результат обмежувача швидкості зміни уставки: сама уставка й ФАКТИЧНО
// застосований вектор повороту (вісь * кут) у зв'язаній системі from.
struct SlewStep {
    Quat target{};
    Vec3 rotation{};
};

[[nodiscard]] inline SlewStep slewLimited(const Quat& from, const Quat& to, float maxAngle) noexcept {
    Quat d = from.conjugate() * to;

    if (d.w < 0.0F) {                       // q і -q — той самий поворот
        d = {-d.w, -d.x, -d.y, -d.z};       // беремо коротшу дугу
    }

    const float vn = d.vec().norm();
    if (vn < 1e-7F) {
        return {to.normalized(), Vec3{}};
    }

    const Vec3 axis = d.vec() * (1.0F / vn);
    const float angle = 2.0F * std::atan2(vn, std::clamp(d.w, -1.0F, 1.0F));

    if (angle <= maxAngle) {
        return {to.normalized(), axis * angle};
    }
    return {(from * Quat::fromAxisAngle(axis, maxAngle)).normalized(), axis * maxAngle};
}

inline constexpr float kGravity = 9.80665F;
inline constexpr float kPi = std::numbers::pi_v<float>;

}  // namespace flight
