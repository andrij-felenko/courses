#include <iostream>
#include <array>
#include <cmath>
#include <iomanip>

// Структура 3D-вектора з RAII та операторами векторної алгебри
struct Vector3 {
    double x{0.0}, y{0.0}, z{0.0};

    constexpr Vector3 operator+(const Vector3& o) const { return {x + o.x, y + o.y, z + o.z}; }
    constexpr Vector3 operator-(const Vector3& o) const { return {x - o.x, y - o.y, z - o.z}; }
    constexpr Vector3 operator*(double s) const { return {x * s, y * s, z * s}; }

    constexpr double dot(const Vector3& o) const { return x * o.x + y * o.y + z * o.z; }
    constexpr Vector3 cross(const Vector3& o) const {
        return {y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x};
    }
    double norm() const { return std::sqrt(dot(*this)); }
};

constexpr Vector3 operator*(double s, const Vector3& v) { return v * s; }

class MonopoleSimulator {
public:
    MonopoleSimulator(double mass, double charge, double monopole_g)
        : m_(mass), q_(charge), g_(monopole_g), mu_((charge * monopole_g) / (4.0 * M_PI)) {}

    Vector3 accel(const Vector3& r, const Vector3& v) const {
        double r_len = r.norm();
        if (r_len < 1e-12) return {0.0, 0.0, 0.0};
        Vector3 vr_cross = v.cross(r);
        return (mu_ / (m_ * r_len * r_len * r_len)) * vr_cross;
    }

    Vector3 poincare_vector(const Vector3& r, const Vector3& v) const {
        double r_len = r.norm();
        if (r_len < 1e-12) return {0.0, 0.0, 0.0};
        Vector3 r_hat = (1.0 / r_len) * r;
        Vector3 L = m_ * r.cross(v);
        return L - mu_ * r_hat;
    }

    void step_rk4(Vector3& r, Vector3& v, double dt) const {
        Vector3 k1_r = v;
        Vector3 k1_v = accel(r, v);

        Vector3 r2 = r + 0.5 * dt * k1_r;
        Vector3 v2 = v + 0.5 * dt * k1_v;
        Vector3 k2_r = v2;
        Vector3 k2_v = accel(r2, v2);

        Vector3 r3 = r + 0.5 * dt * k2_r;
        Vector3 v3 = v + 0.5 * dt * k2_v;
        Vector3 k3_r = v3;
        Vector3 k3_v = accel(r3, v3);

        Vector3 r4 = r + dt * k3_r;
        Vector3 v4 = v + dt * k3_v;
        Vector3 k4_r = v4;
        Vector3 k4_v = accel(r4, v4);

        r = r + (dt / 6.0) * (k1_r + 2.0 * k2_r + 2.0 * k3_r + k4_r);
        v = v + (dt / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v);
    }

    double energy(const Vector3& v) const {
        return 0.5 * m_ * v.dot(v);
    }

private:
    double m_;
    double q_;
    double g_;
    double mu_;
};

int main() {
    MonopoleSimulator sim(1.0, 1.0, 4.0 * M_PI);

    Vector3 r{-5.0, 1.0, 0.0};
    Vector3 v{1.0, 0.0, 0.0};
    double dt = 0.001;
    std::size_t steps = 10000;

    double E0 = sim.energy(v);
    Vector3 J0 = sim.poincare_vector(r, v);

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "E0 = " << E0 << "\n";
    std::cout << "J0 = (" << J0.x << ", " << J0.y << ", " << J0.z << ")\n";

    for (std::size_t i = 0; i < steps; ++i) {
        sim.step_rk4(r, v, dt);
    }

    double E_end = sim.energy(v);
    Vector3 J_end = sim.poincare_vector(r, v);
    Vector3 dJ = J_end - J0;

    std::cout << "\n--- Результати обчислення (C++) ---\n";
    std::cout << "E_end = " << E_end << " (dE = " << std::abs(E_end - E0) << ")\n";
    std::cout << "J_end = (" << J_end.x << ", " << J_end.y << ", " << J_end.z << ")\n";
    std::cout << "|dJ|  = " << dJ.norm() << "\n";

    return 0;
}
