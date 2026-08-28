#include <iostream>
#include <cmath>
#include <iomanip>
#include <string_view>
#include <vector>
#include <numbers>

// Паспортні дані анізотропного одновісного кристала
struct UniaxialCrystal {
    double n_o{1.0};            // Звичайний показник заломлення
    double n_e{1.0};            // Незвичайний показник заломлення
    std::string_view name{};    // Назва кристала

    [[nodiscard]] constexpr double max_birefringence() const noexcept {
        return n_e - n_o;
    }
};

// Результат чисельного простеження променя
struct BirefringenceResult {
    double theta_deg;   // Кут між хвильовим вектором і оптичною віссю (°)
    double n_e_theta;   // Фазовий показник заломлення n_e(θ)
    double walkoff_deg; // Кут зносу Пойнтінга η (°)
    double shift_um;    // Просторовий зсув променя (мкм)
    double ret_rad;     // Фазове запізнення (рад)
    double ret_deg;     // Фазове запізнення у градусах (модуль 360°)
};

class BirefringenceRaytracer {
public:
    // Обчислення оптичних параметрів для заданого кута падіння
    [[nodiscard]] static BirefringenceResult trace_ray(const UniaxialCrystal& crystal,
                                                       double theta_deg,
                                                       double thickness_mm,
                                                       double wavelength_nm) noexcept {
        constexpr double deg2rad = std::numbers::pi / 180.0;
        const double theta = theta_deg * deg2rad;
        const double cos_t = std::cos(theta);
        const double sin_t = std::sin(theta);
        const double tan_t = std::tan(theta);

        // 1. Ефективний показник заломлення n_e(θ)
        const double no2 = crystal.n_o * crystal.n_o;
        const double ne2 = crystal.n_e * crystal.n_e;
        const double denom = std::sqrt(ne2 * cos_t * cos_t + no2 * sin_t * sin_t);
        const double n_e_th = (crystal.n_o * crystal.n_e) / denom;

        // 2. Кут зносу η
        double eta = 0.0;
        if (std::abs(cos_t) > 1e-12 && std::abs(sin_t) > 1e-12) {
            eta = std::atan(((no2 - ne2) * tan_t) / (no2 + ne2 * tan_t * tan_t));
        }

        // 3. Зсув Δ (мкм)
        const double shift = (thickness_mm * 1000.0) * std::tan(std::abs(eta));

        // 4. Різниця фаз Δφ
        const double delta_n = std::abs(n_e_th - crystal.n_o);
        const double phase_ret = (2.0 * std::numbers::pi / (wavelength_nm * 1e-6)) *
                                 (thickness_mm * 1e-3) * delta_n;

        return BirefringenceResult{
            .theta_deg = theta_deg,
            .n_e_theta = n_e_th,
            .walkoff_deg = eta / deg2rad,
            .shift_um = shift,
            .ret_rad = phase_ret,
            .ret_deg = std::fmod(phase_ret / deg2rad, 360.0)
        };
    }

    // Звітність за діапазоном кутів
    static void print_report(const UniaxialCrystal& crystal,
                             double thickness_mm,
                             double wavelength_nm) {
        std::cout << "=========================================================================\n";
        std::cout << " МАТЕРІАЛ: " << crystal.name << "\n";
        std::cout << " Оптичний тип: " << (crystal.max_birefringence() > 0 ? "Позитивний (+)" : "Негативний (-)") << "\n";
        std::cout << " n_o = " << crystal.n_o << ", n_e = " << crystal.n_e
                  << ", Δn = " << crystal.max_birefringence() << "\n";
        std::cout << " Товщина = " << thickness_mm << " мм, Довжина хвилі = " << wavelength_nm << " нм\n";
        std::cout << "=========================================================================\n";
        std::cout << " Кут θ (°) |  n_e(θ)   | Знос η (°) | Зсув Δ (мкм) | Фаза (рад) | Фаза (°) \n";
        std::cout << "-----------+-----------+------------+--------------+------------+----------\n";

        std::cout << std::fixed << std::setprecision(4);
        for (int deg = 0; deg <= 90; deg += 10) {
            const auto res = trace_ray(crystal, static_cast<double>(deg), thickness_mm, wavelength_nm);
            std::cout << "    " << std::setw(2) << deg << "     |  "
                      << res.n_e_theta << " |   "
                      << std::setw(6) << res.walkoff_deg << "   |   "
                      << std::setw(8) << res.shift_um << "   | "
                      << std::setw(10) << res.ret_rad << " |  "
                      << std::setw(6) << std::setprecision(1) << res.ret_deg << "\n"
                      << std::setprecision(4);
        }
        std::cout << "-------------------------------------------------------------------------\n\n";
    }
};

int main() {
    constexpr UniaxialCrystal calcite{
        .n_o = 1.6580,
        .n_e = 1.4864,
        .name = "Кальцит (Iceland Spar)"
    };

    constexpr UniaxialCrystal quartz{
        .n_o = 1.5426,
        .n_e = 1.5517,
        .name = "Кварц (Crystalline Quartz)"
    };

    constexpr double thickness_mm = 10.0;
    constexpr double wavelength_nm = 632.8;

    BirefringenceRaytracer::print_report(calcite, thickness_mm, wavelength_nm);
    BirefringenceRaytracer::print_report(quartz, thickness_mm, wavelength_nm);

    return 0;
}
