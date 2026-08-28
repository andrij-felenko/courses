#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

// Ідіоматичний клас 3D вектора для C++17
struct Vector3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr Vector3D operator+(const Vector3D& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vector3D operator-(const Vector3D& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    [[nodiscard]] constexpr Vector3D operator*(double s) const noexcept {
        return {x * s, y * s, z * s};
    }
    [[nodiscard]] constexpr double dot(const Vector3D& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }
    [[nodiscard]] constexpr Vector3D cross(const Vector3D& o) const noexcept {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }
};

// Клас зарядженої частинки з інкапсуляцією алгоритму Бориса
class ChargedParticle {
public:
    ChargedParticle(Vector3D pos, Vector3D vel, double charge, double mass) noexcept
        : pos_{pos}, vel_{vel}, q_{charge}, m_{mass} {}

    void stepBoris(const Vector3D& E, const Vector3D& B, double dt) noexcept {
        const double qm = q_ / m_;
        
        // 1. Електричний півкрок
        const Vector3D v_minus = vel_ + E * (qm * dt * 0.5);
        
        // 2. Магнітне обертання vectors
        const Vector3D t = B * (qm * dt * 0.5);
        const double t_sq = t.dot(t);
        const Vector3D v_prime = v_minus + v_minus.cross(t);
        const Vector3D s = t * (2.0 / (1.0 + t_sq));
        const Vector3D v_plus = v_minus + v_prime.cross(s);
        
        // 3. Другий електричний півкрок
        vel_ = v_plus + E * (qm * dt * 0.5);
        
        // 4. Оновлення координат
        pos_ = pos_ + vel_ * dt;
    }

    [[nodiscard]] Vector3D getPosition() const noexcept { return pos_; }
    [[nodiscard]] Vector3D getVelocity() const noexcept { return vel_; }
    [[nodiscard]] double getCharge() const noexcept { return q_; }
    [[nodiscard]] double getMass() const noexcept { return m_; }

private:
    Vector3D pos_;
    Vector3D vel_;
    double q_;
    double m_;
};

int main() {
    const Vector3D E{0.0, -100.0, 0.0};
    const Vector3D B{0.0, 0.0, 0.01};
    
    // Створення протона
    ChargedParticle ion({0.0, 0.0, 0.0}, {0.0, 1000.0, 0.0}, 1.60217663e-19, 1.6726219e-27);
    
    const double dt = 1.0e-9;
    const int steps = 10000;
    const Vector3D initial_pos = ion.getPosition();
    
    for (int i = 0; i < steps; ++i) {
        ion.stepBoris(E, B, dt);
    }
    
    const double total_time = steps * dt;
    const double avg_v_drift_x = (ion.getPosition().x - initial_pos.x) / total_time;
    const double theoretical_v_drift_x = 100.0 / 0.01;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "====================================================\n";
    std::cout << "   Чисельне моделювання E x B дрейфу (Мова C++)\n";
    std::cout << "====================================================\n";
    std::cout << "Кінцева позиція іона: (x = " << ion.getPosition().x 
              << " м, y = " << ion.getPosition().y << " м)\n";
    std::cout << "Обчислена середня швидкість дрейфу v_x:  " << avg_v_drift_x << " м/с\n";
    std::cout << "Теоретична швидкість E x B дрейфу:        " << theoretical_v_drift_x << " м/с\n";
    std::cout << "Відносна похибка обчислення:              " 
              << std::abs(avg_v_drift_x - theoretical_v_drift_x) / theoretical_v_drift_x * 100.0 << " %\n";

    return 0;
}
