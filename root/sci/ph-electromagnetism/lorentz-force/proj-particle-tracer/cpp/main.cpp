#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <iomanip>

struct Vector3 {
    double x{0.0}, y{0.0}, z{0.0};

    Vector3 operator+(const Vector3& o) const { return {x + o.x, y + o.y, z + o.z}; }
    Vector3 operator-(const Vector3& o) const { return {x - o.x, y - o.y, z - o.z}; }
    Vector3 operator*(double s) const { return {x * s, y * s, z * s}; }

    static Vector3 cross(const Vector3& a, const Vector3& b) {
        return {
            a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x
        };
    }

    double norm_sq() const { return x * x + y * y + z * z; }
    double norm() const { return std::sqrt(norm_sq()); }
};

struct Particle {
    Vector3 pos;
    Vector3 vel;
    double charge; // Кл
    double mass;   // кг
};

class BorisIntegrator {
public:
    BorisIntegrator(Particle p, Vector3 E, Vector3 B)
        : particle_(std::move(p)), E_(E), B_(B) {}

    void step(double dt) {
        const double q_over_m = particle_.charge / particle_.mass;
        const Vector3 half_E_step = E_ * (q_over_m * dt * 0.5);

        // 1. Половина прискорення від електричного поля
        Vector3 v_minus = particle_.vel + half_E_step;

        // 2. Обертання в магнітному полі (збереження енергії)
        Vector3 t = B_ * (q_over_m * dt * 0.5);
        double t_sq = t.norm_sq();
        Vector3 s = t * (2.0 / (1.0 + t_sq));

        Vector3 v_prime = v_minus + Vector3::cross(v_minus, t);
        Vector3 v_plus = v_minus + Vector3::cross(v_prime, s);

        // 3. Друга половина прискорення від E-поля
        particle_.vel = v_plus + half_E_step;

        // 4. Зсув координат
        particle_.pos = particle_.pos + particle_.vel * dt;
    }

    const Particle& particle() const { return particle_; }

private:
    Particle particle_;
    Vector3 E_;
    Vector3 B_;
};

int main() {
    // Електрон у магнітному полі B_z = 0.01 Тл
    Particle electron{
        .pos = {0.0, 0.0, 0.0},
        .vel = {1e6, 0.0, 2e5}, // v_x = 10^6 м/с, v_z = 2*10^5 м/с
        .charge = -1.60217663e-19,
        .mass = 9.1093837e-31
    };

    Vector3 E{0.0, 0.0, 0.0};
    Vector3 B{0.0, 0.0, 0.01}; // 100 Гаусів

    BorisIntegrator sim(electron, E, B);

    const double dt = 1e-11; // 10 пікосекунд
    const int steps = 1000;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "t[ns]\tx[mm]\ty[mm]\tz[mm]\tE_k[eV]\n";

    for (int i = 0; i <= steps; ++i) {
        if (i % 100 == 0) {
            const auto& p = sim.particle();
            double v_sq = p.vel.norm_sq();
            double e_k_ev = (0.5 * p.mass * v_sq) / 1.60217663e-19;
            std::cout << (i * dt * 1e9) << "\t"
                      << (p.pos.x * 1000.0) << "\t"
                      << (p.pos.y * 1000.0) << "\t"
                      << (p.pos.z * 1000.0) << "\t"
                      << e_k_ev << "\n";
        }
        sim.step(dt);
    }
    return 0;
}
