#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <iomanip>
#include <algorithm>

struct YagiElement {
    std::string name;
    double position_m;
    double length_m;
};

class YagiCalculator {
public:
    struct Configuration {
        double frequency_mhz;
        int num_directors;
        double element_diameter_mm;
    };

    struct Result {
        double frequency_mhz;
        double wavelength_m;
        double boom_length_m;
        std::vector<YagiElement> elements;
    };

    static Result calculate(const Configuration& config) {
        Result res{};
        res.frequency_mhz = config.frequency_mhz;
        res.wavelength_m = 299.792458 / config.frequency_mhz;

        const double ratio = (config.element_diameter_mm / 1000.0) / res.wavelength_m;
        double k_v = 0.95 - 0.02 * std::log10(ratio > 1e-4 ? ratio : 1e-4);
        k_v = std::clamp(k_v, 0.91, 0.98);

        const double lambda = res.wavelength_m;
        double current_z = 0.0;

        // 1. Рефлектор
        res.elements.push_back({"Рефлектор", current_z, 0.485 * lambda * k_v});

        // 2. Активний диполь
        current_z += 0.18 * lambda;
        res.elements.push_back({"Активний диполь", current_z, 0.455 * lambda * k_v});

        // 3. Директори
        double dir_spacing = 0.15 * lambda;
        for (int i = 0; i < config.num_directors; ++i) {
            current_z += dir_spacing;
            double factor = std::max(0.370, 0.420 - 0.008 * i);
            res.elements.push_back({
                "Директор " + std::to_string(i + 1),
                current_z,
                factor * lambda * k_v
            });
            dir_spacing = std::min(0.28 * lambda, (0.15 + 0.01 * (i + 1)) * lambda);
        }

        res.boom_length_m = current_z;
        return res;
    }
};

int main() {
    YagiCalculator::Configuration config{
        .frequency_mhz = 433.92,
        .num_directors = 4,
        .element_diameter_mm = 6.0
    };

    auto res = YagiCalculator::calculate(config);

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "=========================================================\n";
    std::cout << "  РОЗРАХУНОК АНТЕНИ ЯҐІ-УДА ДЛЯ ЧАСТОТИ " << res.frequency_mhz << " МГц\n";
    std::cout << "  Довжина хвилі λ = " << (res.wavelength_m * 100.0) << " см\n";
    std::cout << "  Довжина траверси = " << (res.boom_length_m * 1000.0) << " мм\n";
    std::cout << "=========================================================\n";
    std::cout << std::left << std::setw(18) << "Елемент" << " | "
              << std::right << std::setw(18) << "Позиція (мм)" << " | "
              << std::setw(14) << "Довжина L (мм)" << "\n";
    std::cout << "---------------------------------------------------------\n";

    for (const auto& elem : res.elements) {
        std::cout << std::left << std::setw(18) << elem.name << " | "
                  << std::right << std::setw(18) << (elem.position_m * 1000.0) << " | "
                  << std::setw(14) << (elem.length_m * 1000.0) << "\n";
    }
    std::cout << "=========================================================\n";

    return 0;
}
