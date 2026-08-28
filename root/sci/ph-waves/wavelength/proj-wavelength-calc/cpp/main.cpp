#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <format>
#include <expected>

constexpr double SPEED_OF_LIGHT_VACUUM = 299792458.0;

struct WaveProperties {
    double frequency_hz;
    double speed_m_s;
    double wavelength_m;
    double wavenumber_k; // просторова частота, рад/м
    double period_s;
};

enum class WaveError {
    InvalidFrequency,
    InvalidSpeed,
    InvalidRefractiveIndex
};

class WaveCalculator {
public:
    // Обчислення швидкості звуку у сухий атмосфері (°C)
    [[nodiscard]] static constexpr double acoustic_speed_air(double temp_celsius) noexcept {
        return 331.3 * std::sqrt(1.0 + temp_celsius / 273.15);
    }

    // Обчислення параметрів хвилі з використанням std::expected (C++23)
    [[nodiscard]] static std::expected<WaveProperties, WaveError> compute(double frequency_hz, double speed_m_s) noexcept {
        if (frequency_hz <= 0.0) return std::unexpected(WaveError::InvalidFrequency);
        if (speed_m_s <= 0.0) return std::unexpected(WaveError::InvalidSpeed);

        const double wavelength = speed_m_s / frequency_hz;
        const double wavenumber = (2.0 * std::numbers::pi) / wavelength;
        const double period = 1.0 / frequency_hz;

        return WaveProperties{
            .frequency_hz = frequency_hz,
            .speed_m_s = speed_m_s,
            .speed_m_s = speed_m_s,
            .wavelength_m = wavelength,
            .wavenumber_k = wavenumber,
            .period_s = period
        };
    }

    // Генерація списку координат вузлів стоячої хвилі
    [[nodiscard]] static std::vector<double> standing_wave_nodes(double length_m, double wavelength_m) {
        std::vector<double> nodes;
        if (wavelength_m <= 0.0 || length_m < 0.0) return nodes;

        const double spacing = wavelength_m / 2.0;
        for (double pos = 0.0; pos <= length_m + 1e-9; pos += spacing) {
            nodes.push_back(pos);
        }
        return nodes;
    }
};

int main() {
    const double v_air = WaveCalculator::acoustic_speed_air(20.0);
    auto us_res = WaveCalculator::compute(40000.0, v_air);

    if (us_res) {
        std::cout << "=== 1. Акустика (40 кГц у повітрі 20°C) ===\n";
        std::cout << "Швидкість звуку: " << us_res->speed_m_s << " м/с\n";
        std::cout << "Довжина хвилі: " << (us_res->wavelength_m * 1000.0) << " мм\n";
        std::cout << "Хвильове число k: " << us_res->wavenumber_k << " рад/м\n";
    }

    const double em_speed = SPEED_OF_LIGHT_VACUUM / 1.444;
    auto opt_res = WaveCalculator::compute(193.4e12, em_speed);
    if (opt_res) {
        std::cout << "\n=== 2. Волоконна оптика (193.4 ТГц) ===\n";
        std::cout << "Довжина хвилі: " << (opt_res->wavelength_m * 1e9) << " нм\n";
        std::cout << "Хвильове число k: " << opt_res->wavenumber_k << " рад/м\n";
    }

    const double lambda_500 = v_air / 500.0;
    auto nodes = WaveCalculator::standing_wave_nodes(1.0, lambda_500);
    std::cout << "\n=== 3. Вузли стоячої хвилі (500 Гц, L = 1.0 м) ===\n";
    for (size_t i = 0; i < nodes.size(); ++i) {
        std::cout << "Вузол " << (i + 1) << ": " << nodes[i] << " м\n";
    }

    return 0;
}
