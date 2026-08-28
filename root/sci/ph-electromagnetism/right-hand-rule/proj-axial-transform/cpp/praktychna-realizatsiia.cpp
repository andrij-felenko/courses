#include <iostream>
#include <array>
#include <string_view>
#include <cmath>

enum class VectorKind {
    Polar,
    Axial
};

struct Matrix3x3 {
    std::array<std::array<double, 3>, 3> m{};

    [[nodiscard]] constexpr double determinant() const noexcept {
        return m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
             - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
             + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
    }

    static constexpr Matrix3x3 identity() noexcept {
        return Matrix3x3{{
            {{1.0, 0.0, 0.0}},
            {{0.0, 1.0, 0.0}},
            {{0.0, 0.0, 1.0}}
        }};
    }

    static constexpr Matrix3x3 inversion() noexcept {
        return Matrix3x3{{
            {{-1.0,  0.0,  0.0}},
            {{ 0.0, -1.0,  0.0}},
            {{ 0.0,  0.0, -1.0}}
        }};
    }
};

class PhysicsVector {
public:
    double x{0.0};
    double y{0.0};
    double z{0.0};
    VectorKind kind{VectorKind::Polar};

    constexpr PhysicsVector(double x_, double y_, double z_, VectorKind k) noexcept
        : x(x_), y(y_), z(z_), kind(k) {}

    [[nodiscard]] PhysicsVector cross(const PhysicsVector& rhs) const noexcept {
        const double cx = y * rhs.z - z * rhs.y;
        const double cy = z * rhs.x - x * rhs.z;
        const double cz = x * rhs.y - y * rhs.x;

        const VectorKind res_kind = (kind == rhs.kind) ? VectorKind::Axial : VectorKind::Polar;
        return PhysicsVector{cx, cy, cz, res_kind};
    }

    [[nodiscard]] PhysicsVector transform(const Matrix3x3& mat) const noexcept {
        double rx = mat.m[0][0] * x + mat.m[0][1] * y + mat.m[0][2] * z;
        double ry = mat.m[1][0] * x + mat.m[1][1] * y + mat.m[1][2] * z;
        double rz = mat.m[2][0] * x + mat.m[2][1] * y + mat.m[2][2] * z;

        if (kind == VectorKind::Axial) {
            const double det = mat.determinant();
            rx *= det;
            ry *= det;
            rz *= det;
        }

        return PhysicsVector{rx, ry, rz, kind};
    }

    void print(std::string_view label) const {
        const std::string_view kind_str = (kind == VectorKind::Polar) ? "Полярний" : "Аксіальний";
        std::cout << label << " [" << kind_str << "]: ("
                  << x << ", " << y << ", " << z << ")\n";
    }
};

int main() {
    const PhysicsVector v{1.0, 2.0, 3.0, VectorKind::Polar};
    const PhysicsVector B{0.0, 0.0, 5.0, VectorKind::Axial};

    v.print("Початковий v");
    B.print("Початкове B");

    const PhysicsVector F = v.cross(B);
    F.print("Сила Лоренца F = v × B");

    constexpr Matrix3x3 inv_mat = Matrix3x3::inversion();

    std::cout << "\n--- Трансформація при інверсії координат (det = -1) ---\n";
    const PhysicsVector v_prime = v.transform(inv_mat);
    const PhysicsVector B_prime = B.transform(inv_mat);
    const PhysicsVector F_prime = F.transform(inv_mat);

    v_prime.print("Трансформований v'");
    B_prime.print("Трансформоване B'");
    F_prime.print("Трансформована F'");

    const PhysicsVector F_recalc = v_prime.cross(B_prime);
    F_recalc.print("Обчислена F_recalc = v' × B'");

    return 0;
}
