#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <algorithm>

struct SimulationFrame {
    double time_us;
    double radius_mm;
    double velocity_kms;
    double b_field_tesla;
};

struct BennettPoint {
    double r_mm;
    double n_relative;
    double b_field_tesla;
};

class ZPinchDynamicsEngine {
public:
    ZPinchDynamicsEngine(double current_peak_amp, double initial_radius_m, double gas_density_kg_m3)
        : I0_(current_peak_amp), R0_(initial_radius_m), rho0_(gas_density_kg_m3) {}

    std::vector<SimulationFrame> execute(double total_time_s, double dt_s) {
        std::vector<SimulationFrame> log;
        const double omega = 2.0 * std::numbers::pi * 1e6; // 1 MHz
        const double mu0 = 4.0 * std::numbers::pi * 1e-7;
        const double p0 = 100.0; // initial pressure (Pa)

        double R = R0_ * 0.999;
        double v = 0.0;
        double t = 0.0;

        const size_t num_steps = static_cast<size_t>(total_time_s / dt_s);
        log.reserve(num_steps);

        for (size_t i = 0; i < num_steps; ++i) {
            double I_t = (t < std::numbers::pi / omega) ? I0_ * std::sin(omega * t) : 0.0;
            
            // Snowplow accumulated mass
            double M_L = std::numbers::pi * (R0_ * R0_ - R * R) * rho0_ + 1e-12;

            double f_mag = (R > 1e-6) ? -(mu0 * I_t * I_t) / (4.0 * std::numbers::pi * R) : 0.0;
            double p_th = p0 * std::pow(R0_ / R, 10.0 / 3.0);
            double f_th = 2.0 * std::numbers::pi * R * p_th;

            double accel = (f_mag + f_th) / M_L;

            // Symplectic Euler integration step
            v += accel * dt_s;
            R += v * dt_s;

            // Singularity limit & dissipative rebound at axis
            if (R < 0.005 * R0_) {
                R = 0.005 * R0_;
                v = -0.4 * v;
            }

            double B_surf = (R > 1e-6) ? (mu0 * std::abs(I_t)) / (2.0 * std::numbers::pi * R) : 0.0;

            log.push_back({t * 1e6, R * 1e3, v * 1e-3, B_surf});
            t += dt_s;
        }

        return log;
    }

    static std::vector<BennettPoint> calculate_bennett_equilibrium(double r_max, size_t points, double a, double I_total) {
        std::vector<BennettPoint> profile;
        profile.reserve(points);
        const double mu0 = 4.0 * std::numbers::pi * 1e-7;
        const double dr = r_max / static_cast<double>(points);

        for (size_t i = 0; i < points; ++i) {
            double r = static_cast<double>(i) * dr;
            double n_rel = 1.0 / std::pow(1.0 + (r / a) * (r / a), 2.0);
            double B_phi = (mu0 * I_total / (2.0 * std::numbers::pi)) * (r / (r * r + a * a));
            profile.push_back({r * 1e3, n_rel, B_phi});
        }
        return profile;
    }

private:
    double I0_;
    double R0_;
    double rho0_;
};

int main() {
    ZPinchDynamicsEngine engine(100e3, 0.02, 1e-4); // 100 kA, 2 cm, 0.1 g/m³
    auto frames = engine.execute(1e-6, 5e-10);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== СИМУЛЯЦІЯ Z-ПІНЧУ (C++20 Engine) ===\n";
    std::cout << "Успішно обраховано " << frames.size() << " часових кроків.\n\n";
    
    std::cout << "Перші 5 кроків еволюції:\n";
    for (size_t i = 0; i < 5 && i < frames.size(); ++i) {
        std::cout << "t = " << frames[i].time_us << " мкс | R = " 
                  << frames[i].radius_mm << " мм | V = " 
                  << frames[i].velocity_kms << " км/с | B = " 
                  << frames[i].b_field_tesla << " Тл\n";
    }

    auto profile = ZPinchDynamicsEngine::calculate_bennett_equilibrium(0.01, 100, 0.002, 100e3);
    std::cout << "\nПрофіль Беннетта успішно сформовано (" << profile.size() << " точок).\n";

    return 0;
}
