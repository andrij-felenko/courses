#include <iostream>
#include <cmath>
#include <optional>
#include <iomanip>
#include <algorithm>

namespace iono {

struct PathParams {
    double electron_density_m3;  // Електронна густина (ел/м³)
    double layer_height_km;      // Висота відбивального шару (км)
    double target_distance_km;   // Відстань між станціями (км)
    double operational_freq_mhz; // Обрана робоча частота (МГц)
};

struct PathMetrics {
    double critical_freq_mhz{0.0};
    double muf_mhz{0.0};
    double muf_factor{0.0};
    double owf_mhz{0.0};
    std::optional<double> skip_distance_km{std::nullopt};
};

class IonosphereCalculator {
public:
    static constexpr double EarthRadiusKm = 6371.0;

    [[nodiscard]] static PathMetrics compute(const PathParams& params) noexcept {
        PathMetrics metrics{};
        
        // 1. Критична частота
        const double f_c_hz = 8.98 * std::sqrt(params.electron_density_m3);
        metrics.critical_freq_mhz = f_c_hz / 1.0e6;
        
        // 2. Геометрія похилого променя
        const double half_d = params.target_distance_km / 2.0;
        const double theta_flat = std::atan2(half_d, params.layer_height_km);
        
        const double sin_sph = std::sin(theta_flat) * (EarthRadiusKm / (EarthRadiusKm + params.layer_height_km));
        const double cos_sph = std::sqrt(1.0 - std::min(1.0, sin_sph * sin_sph));
        
        metrics.muf_factor = 1.0 / cos_sph;
        metrics.muf_mhz = metrics.critical_freq_mhz * metrics.muf_factor;
        metrics.owf_mhz = 0.85 * metrics.muf_mhz;
        
        // 3. Відстань стрибка для обраної частоти
        if (params.operational_freq_mhz <= metrics.critical_freq_mhz) {
            metrics.skip_distance_km = 0.0; // Покриття починається від передавача
        } else if (params.operational_freq_mhz <= metrics.muf_mhz) {
            const double sec_req = params.operational_freq_mhz / metrics.critical_freq_mhz;
            const double cos_req = 1.0 / sec_req;
            const double sin_req = std::sqrt(1.0 - cos_req * cos_req);
            metrics.skip_distance_km = 2.0 * params.layer_height_km * (sin_req / cos_req);
        } else {
            metrics.skip_distance_km = std::nullopt; // Пробиває іоносферу
        }
        
        return metrics;
    }
};

} // namespace iono

int main() {
    iono::PathParams params{
        .electron_density_m3 = 1.2e12,
        .layer_height_km = 300.0,
        .target_distance_km = 2000.0,
        .operational_freq_mhz = 14.150
    };

    const auto res = iono::IonosphereCalculator::compute(params);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== РЕЗУЛЬТАТИ РОЗРАХУНКУ ІОНОСФЕРНОЇ ТРАСИ (C++) ===\n";
    std::cout << "Критична частота f_c : " << res.critical_freq_mhz << " МГц\n";
    std::cout << "MUF-фактор           : " << res.muf_factor << "\n";
    std::cout << "Максимальна частота MUF: " << res.muf_mhz << " МГц\n";
    std::cout << "Оптимальна частота OWF: " << res.owf_mhz << " МГц\n";
    std::cout << "Робоча частота f_op  : " << params.operational_freq_mhz << " МГц\n";

    if (res.skip_distance_km.has_value()) {
        std::cout << "Статус: ВІДБИТТЯ УСПІШНЕ\n";
        std::cout << "Відстань стрибка D_skip: " << *res.skip_distance_km << " км\n";
    } else {
        std::cout << "Статус: ПРОБИВАННЯ ІОНОСФЕРИ (сигнал вилітає у космос)\n";
    }

    return 0;
}
