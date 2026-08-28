#include <cmath>
#include <optional>

struct Vector3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr double dot(const Vector3& rhs) const noexcept {
        return x * rhs.x + y * rhs.y + z * rhs.z;
    }

    [[nodiscard]] constexpr Vector3 operator+(const Vector3& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }

    [[nodiscard]] constexpr Vector3 operator*(double scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }

    [[nodiscard]] constexpr Vector3 operator-() const noexcept {
        return {-x, -y, -z};
    }
};

/*
 * Обчислює вектор заломленого променя за допомогою векторного закону Снелла.
 * Повертає std::optional<Vector3>, що містить нормований вектор T або std::nullopt при ПВВ.
 */
[[nodiscard]] std::optional<Vector3> refract(const Vector3& I,
                                            const Vector3& N,
                                            double eta) noexcept {
    double cos_i = -I.dot(N);
    Vector3 oriented_N = N;

    if (cos_i < 0.0) {
        cos_i = -cos_i;
        oriented_N = -N;
    }

    const double k = 1.0 - eta * eta * (1.0 - cos_i * cos_i);
    if (k < 0.0) {
        // Повне внутрішнє відбиття (Total Internal Reflection)
        return std::nullopt;
    }

    const double cos_t = std::sqrt(k);
    return I * eta + oriented_N * (eta * cos_i - cos_t);
}
