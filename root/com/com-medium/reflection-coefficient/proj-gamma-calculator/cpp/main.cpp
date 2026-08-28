#include <iostream>
#include <complex>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <iomanip>

namespace rf {

// Структура фізичних параметрів лінії передачі
struct LineParams {
    double z0 = 50.0;              // Хвильовий опір лінії (Ом)
    double frequency_hz = 1e9;     // Частота сигналу (Гц)
    double length_m = 0.0;         // Фізична довжина лінії (м)
    double velocity_factor = 0.66; // Коефіцієнт укорочення хвилі
    double attenuation_db_m = 0.0; // Згасання лінії (дБ/м)
};

// Повний підсумок розрахунку ВЧ-тракту
struct ReflectionResult {
    std::complex<double> gamma_load; // Комплексний Γ на навантаженні
    double gamma_mag;                // Модуль |Γ|
    double gamma_phase_deg;         // Фаза Γ (градуси)
    double vswr;                     // КСХ (VSWR)
    double return_loss_db;           // Втрати на відбиття (дБ)
    double mismatch_loss_db;         // Втрати на неузгодженні (дБ)
    double power_transmitted_pct;    // Передана потужність (%)
    double power_reflected_pct;      // Відбита потужність (%)
    std::complex<double> gamma_input;// Комплексний Γ на вході лінії
    std::complex<double> z_input;    // Вхідний імпеданс Z_in (Ом)
};

// Типізована перелічувана помилка розрахунку
enum class RfError {
    InvalidZ0,
    InvalidFrequency,
    InvalidVelocityFactor,
    InvalidLength
};

[[nodiscard]] constexpr std::string_view to_string(RfError err) noexcept {
    switch (err) {
        case RfError::InvalidZ0: 
            return "Хвильовий опір Z0 має бути суворо додатним";
        case RfError::InvalidFrequency: 
            return "Частота сигналу має бути додатною";
        case RfError::InvalidVelocityFactor: 
            return "Коефіцієнт укорочення має бути в межах (0.0, 1.0]";
        case RfError::InvalidLength: 
            return "Довжина лінії не може бути від'ємною";
    }
    return "Невідома помилка розрахунку";
}

// Головна функція обчислення параметрів неузгодження (C++23 std::expected)
[[nodiscard]] std::expected<ReflectionResult, RfError> calculate_reflection(
    std::complex<double> z_load,
    const LineParams& line) noexcept 
{
    if (line.z0 <= 0.0) return std::unexpected(RfError::InvalidZ0);
    if (line.frequency_hz <= 0.0) return std::unexpected(RfError::InvalidFrequency);
    if (line.velocity_factor <= 0.0 || line.velocity_factor > 1.0) {
        return std::unexpected(RfError::InvalidVelocityFactor);
    }
    if (line.length_m < 0.0) return std::unexpected(RfError::InvalidLength);

    constexpr double c0 = 299792458.0; // Швидкість світла у вакуумі (м/с)
    const double v_phase = c0 * line.velocity_factor;
    const double wavelength = v_phase / line.frequency_hz;
    const double beta = 2.0 * std::numbers::pi / wavelength; // Фазова стала (рад/м)

    // Переведення згасання з дБ/м у Непери/м (1 Нп ≈ 8.685889638 дБ)
    const double alpha_np_m = line.attenuation_db_m / 8.685889638;

    // 1. Коефіцієнт відбиття на навантаженні: Γ_L = (Z_L - Z0) / (Z_L + Z0)
    const std::complex<double> gamma_l = (z_load - line.z0) / (z_load + line.z0);
    const double mag = std::abs(gamma_l);
    const double phase_deg = std::arg(gamma_l) * 180.0 / std::numbers::pi;

    // 2. КСХ = (1 + |Γ|) / (1 - |Γ|) з захистом від ділення на нуль
    const double vswr = (mag >= 0.99999) ? 999.99 : (1.0 + mag) / (1.0 - mag);

    // 3. Return Loss (дБ) = -20 * log10(|Γ|) з захистом від log(0)
    const double return_loss = (mag < 1e-12) ? 240.0 : -20.0 * std::log10(mag);

    // 4. Енергетичні співвідношення потужностей
    const double p_ref_pct = mag * mag * 100.0;
    const double p_trans_pct = (1.0 - mag * mag) * 100.0;
    const double mismatch_loss = (mag >= 0.99999) ? 99.99 : -10.0 * std::log10(1.0 - mag * mag);

    // 5. Трансформація Γ вздовж лінії: Γ(l) = Γ_L * exp(-2*alpha*l - j*2*beta*l)
    const std::complex<double> gamma_prop{ -2.0 * alpha_np_m * line.length_m,
                                           -2.0 * beta * line.length_m };
    const std::complex<double> gamma_in = gamma_l * std::exp(gamma_prop);

    // 6. Вхідний імпеданс Z_in = Z0 * (1 + Γ_in) / (1 - Γ_in)
    const std::complex<double> z_in = line.z0 * (1.0 + gamma_in) / (1.0 - gamma_in);

    return ReflectionResult{
        .gamma_load = gamma_l,
        .gamma_mag = mag,
        .gamma_phase_deg = phase_deg,
        .vswr = vswr,
        .return_loss_db = return_loss,
        .mismatch_loss_db = mismatch_loss,
        .power_transmitted_pct = p_trans_pct,
        .power_reflected_pct = p_ref_pct,
        .gamma_input = gamma_in,
        .z_input = z_in
    };
}

} // namespace rf

int main() {
    using namespace std::complex_literals;

    // Приклад: навантаження 75 + j25 Ом підключено через 5 см FR4 траси (2.4 ГГц)
    const std::complex<double> z_load = 75.0 + 25.0j;
    const rf::LineParams line{
        .z0 = 50.0,
        .frequency_hz = 2.4e9,       // 2.4 ГГц (Wi-Fi / Bluetooth)
        .length_m = 0.05,            // 5 см лінія
        .velocity_factor = 0.60,     // Склотекстоліт FR4
        .attenuation_db_m = 1.5      // 1.5 дБ/м згасання
    };

    const auto res = rf::calculate_reflection(z_load, line);
    if (!res) {
        std::cerr << "Помилка: " << rf::to_string(res.error()) << '\n';
        return 1;
    }

    std::cout << std::fixed << std::setprecision(4)
              << "=== ДІАГНОСТИКА ВЧ-ТРАКТУ (C++23) ===\n"
              << "Γ навантаження: " << res->gamma_load.real() << " + j(" 
              << res->gamma_load.imag() << ")\n"
              << "Модуль |Γ|:      " << res->gamma_mag << '\n'
              << "Фаза Γ:          " << res->gamma_phase_deg << " deg\n"
              << "КСХ (VSWR):      " << res->vswr << " : 1\n"
              << "Return Loss:     " << res->return_loss_db << " dB\n"
              << "Mismatch Loss:   " << res->mismatch_loss_db << " dB\n"
              << "Передано P:      " << res->power_transmitted_pct << " %\n"
              << "Відбито P:       " << res->power_reflected_pct << " %\n"
              << "Γ на вході:      " << res->gamma_input.real() << " + j(" 
              << res->gamma_input.imag() << ")\n"
              << "Z вхідне:        " << res->z_input.real() << " + j(" 
              << res->z_input.imag() << ") Ohm\n";
    return 0;
}
