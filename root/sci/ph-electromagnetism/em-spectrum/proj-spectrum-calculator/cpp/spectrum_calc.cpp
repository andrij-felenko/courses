// 
// spectrum_calc.cpp — Об'єктно-орієнтований модуль аналізу спектра за стандартом C++20
// Модуль використовує constexpr обчислення, std::string_view, строго типізовані enum class
// 
#include <iostream>
#include <cmath>
#include <string_view>
#include <numbers>
#include <iomanip>
#include <array>

namespace physics::em {

// Фундаментальні константи у просторі імен
constexpr double c_speed    = 299792458.0;
constexpr double h_planck   = 6.62607015e-34;
constexpr double ev_joule   = 1.602176634e-19;
constexpr double wien_const = 2.89777195e-3;
constexpr double cu_sigma   = 5.8e7;
constexpr double mu_0       = 4.0 * std::numbers::pi * 1e-7;

enum class SpectralBand {
    Radio,
    Microwave,
    Infrared,
    Visible,
    Ultraviolet,
    XRay,
    Gamma
};

[[nodiscard]] constexpr std::string_view to_string(SpectralBand band) noexcept {
    switch (band) {
        case SpectralBand::Radio:       return "Радіохвилі (Radio)";
        case SpectralBand::Microwave:   return "Мікрохвилі (Microwave / НВЧ)";
        case SpectralBand::Infrared:    return "Інфрачервоне (IR)";
        case SpectralBand::Visible:     return "Видиме світло (Visible)";
        case SpectralBand::Ultraviolet: return "Ультрафіолет (UV)";
        case SpectralBand::XRay:        return "Рентгенівське (X-Ray)";
        case SpectralBand::Gamma:       return "Гамма-випромінювання (Gamma)";
    }
    return "Невідомий діапазон";
}

struct SpectrumRecord {
    double frequency_hz;
    double wavelength_m;
    double energy_ev;
    double skin_depth_cu_m;
    double wien_temp_k;
    SpectralBand band;
    bool is_ionizing;

    [[nodiscard]] static constexpr SpectrumRecord from_frequency(double freq_hz) noexcept {
        const double safe_freq = (freq_hz > 0.0) ? freq_hz : 1e-12;
        const double lambda = c_speed / safe_freq;
        const double energy_j = h_planck * safe_freq;
        const double energy_ev = energy_j / ev_joule;
        const double omega = 2.0 * std::numbers::pi * safe_freq;
        const double skin_m = std::sqrt(2.0 / (omega * mu_0 * cu_sigma));
        const double temp_k = wien_const / lambda;

        SpectralBand band = SpectralBand::Radio;
        if (safe_freq >= 3.0e19)      band = SpectralBand::Gamma;
        else if (safe_freq >= 3.0e16) band = SpectralBand::XRay;
        else if (safe_freq >= 7.9e14) band = SpectralBand::Ultraviolet;
        else if (safe_freq >= 4.0e14) band = SpectralBand::Visible;
        else if (safe_freq >= 3.0e11) band = SpectralBand::Infrared;
        else if (safe_freq >= 3.0e9)  band = SpectralBand::Microwave;

        return SpectrumRecord{
            .frequency_hz = safe_freq,
            .wavelength_m = lambda,
            .energy_ev = energy_ev,
            .skin_depth_cu_m = skin_m,
            .wien_temp_k = temp_k,
            .band = band,
            .is_ionizing = (energy_ev >= 10.0)
        };
    }

    [[nodiscard]] static constexpr SpectrumRecord from_wavelength(double wavelength_m) noexcept {
        const double safe_lambda = (wavelength_m > 0.0) ? wavelength_m : 1e-18;
        return from_frequency(c_speed / safe_lambda);
    }
};

void print_record(const SpectrumRecord& rec) {
    std::cout << "\n--------------------------------------------------\n";
    std::cout << "  ПАСПОРТНА КАРТКА СИГНАЛУ (C++20 Module)        \n";
    std::cout << "--------------------------------------------------\n";
    std::cout << std::scientific << std::setprecision(4);
    std::cout << " Частота:          " << rec.frequency_hz << " Гц\n";
    std::cout << " Довжина хвилі:   " << rec.wavelength_m << " м\n";
    std::cout << " Енергія фотона:  " << rec.energy_ev << " еВ\n";
    std::cout << " Скін-шар у міді: " << rec.skin_depth_cu_m << " м\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << " Температура Віна: " << rec.wien_temp_k << " K\n";
    std::cout << " Діапазон:         " << to_string(rec.band) << "\n";
    std::cout << " Іонізуюче:        " << (rec.is_ionizing ? "ТАК [Вимоги захисту]" : "НІ [Безпечно]") << "\n";
    std::cout << "--------------------------------------------------\n";
}

} // namespace physics::em

int main() {
    using namespace physics::em;

    std::cout << "Спектральний аналіз (C++20):\n";

    // Тест 1: EUV Літографія 13.5 нм
    auto euv_chip = SpectrumRecord::from_wavelength(13.5e-9);
    print_record(euv_chip);

    // Тест 2: Позитронна анігіляція 511 кеВ (Гамма)
    constexpr double gamma_freq = (511.0e3 * ev_joule) / h_planck;
    auto gamma_annihilation = SpectrumRecord::from_frequency(gamma_freq);
    print_record(gamma_annihilation);

    return 0;
}
