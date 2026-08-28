#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <numbers>
#include <iomanip>

namespace aeroacoustics {

constexpr double kPref = 20e-6;        // 20 мкПа (поріг чутності)
constexpr double kRhoAir = 1.225;      // кг/м³
constexpr double kSoundSpeed = 343.0;  // м/с (повітря 20 °C)

struct PropellerSpec {
    double diameter_m{0.254};
    int num_blades{2};
    double rpm{6000.0};
    double thrust_n{7.5};
    double power_w{85.0};
    double chord_m{0.022};
    double thickness_m{0.0025};
    double distance_m{10.0};
    double directivity_angle_deg{110.0};
};

struct HarmonicDetail {
    int index{0};
    double frequency_hz{0.0};
    double spl_db{0.0};
    double spl_dba{0.0};
};

struct AcousticReport {
    double bpf_hz{0.0};
    double tip_speed_mps{0.0};
    double tip_mach{0.0};
    std::vector<HarmonicDetail> harmonics;
    double broadband_peak_hz{0.0};
    double broadband_spl_db{0.0};
    double total_spl_db{0.0};
    double total_spl_dba{0.0};
};

// Обчислення функції Бесселя першого роду J_n(x) степеневим рядом
[[nodiscard]] constexpr double bessel_jn(int n, double x) noexcept {
    if (n < 0) {
        return (n % 2 == 0) ? bessel_jn(-n, x) : -bessel_jn(-n, x);
    }
    if (x == 0.0) {
        return (n == 0) ? 1.0 : 0.0;
    }
    
    const double half_x = 0.5 * x;
    double term = 1.0;
    for (int i = 1; i <= n; ++i) {
        term *= (half_x / static_cast<double>(i));
    }
    
    double sum = term;
    const double half_x_sq = half_x * half_x;
    for (int k = 1; k < 60; ++k) {
        term *= -half_x_sq / (static_cast<double>(k) * static_cast<double>(n + k));
        sum += term;
        if (std::abs(term) < 1e-15 * std::abs(sum)) {
            break;
        }
    }
    return sum;
}

// Фільтр частотної корекції A-зважування (IEC 61672-1)
[[nodiscard]] inline double calculate_a_weighting(double freq_hz) noexcept {
    if (freq_hz < 10.0) return -70.0;
    const double f2 = freq_hz * freq_hz;
    const double num = 12194.0 * 12194.0 * f2 * f2;
    const double den = (f2 + 20.6 * 20.6) * 
                       std::sqrt((f2 + 107.7 * 107.7) * (f2 + 737.9 * 737.9)) * 
                       (f2 + 12194.0 * 12194.0);
    return 20.0 * std::log10(num / den) + 2.0;
}

// Розрахунок повної акустичної моделі
[[nodiscard]] AcousticReport evaluate_propeller_noise(const PropellerSpec& spec, int num_harmonics = 6) {
    AcousticReport report;
    const double radius = 0.5 * spec.diameter_m;
    const double r_eff = 0.80 * radius;
    const double n_rps = spec.rpm / 60.0;
    const double omega = 2.0 * std::numbers::pi * n_rps;
    
    report.bpf_hz = static_cast<double>(spec.num_blades) * n_rps;
    report.tip_speed_mps = omega * radius;
    report.tip_mach = report.tip_speed_mps / kSoundSpeed;
    
    const double theta_rad = spec.directivity_angle_deg * std::numbers::pi / 180.0;
    const double sin_theta = std::sin(theta_rad);
    const double cos_theta = std::cos(theta_rad);
    
    const double torque = (omega > 0.0) ? (spec.power_w / omega) : 0.0;
    const double blade_volume = spec.chord_m * spec.thickness_m * radius * 0.68;
    const double m_eff = 0.80 * report.tip_mach;
    
    double linear_energy_sum = 0.0;
    double a_weighted_energy_sum = 0.0;
    
    report.harmonics.reserve(num_harmonics);
    for (int m = 1; m <= num_harmonics; ++m) {
        const int order = m * spec.num_blades;
        const double freq = static_cast<double>(m) * report.bpf_hz;
        const double arg_bessel = static_cast<double>(order) * m_eff * sin_theta;
        const double j_val = bessel_jn(order, arg_bessel);
        
        // 1. Шум навантаження (диполь Гутіна)
        const double gutin_bracket = -spec.thrust_n * cos_theta + 
                                     (kSoundSpeed * torque) / (omega * r_eff * r_eff);
        const double p_load = (static_cast<double>(order) * omega / 
                              (2.0 * std::numbers::sqrt2 * std::numbers::pi * kSoundSpeed * spec.distance_m)) *
                              gutin_bracket * j_val;
                              
        // 2. Шум товщини (монополь Демінга)
        const double p_thick = -(kRhoAir * std::pow(static_cast<double>(order) * omega, 2) / 
                                (2.0 * std::numbers::sqrt2 * std::numbers::pi * spec.distance_m)) *
                                blade_volume * j_val;
                                
        const double p_total = std::max(1e-12, std::sqrt(p_load * p_load + p_thick * p_thick));
        const double spl_db = 20.0 * std::log10(p_total / kPref);
        const double spl_dba = spl_db + calculate_a_weighting(freq);
        
        report.harmonics.push_back({m, freq, spl_db, spl_dba});
        linear_energy_sum += std::pow(10.0, spl_db / 10.0);
        a_weighted_energy_sum += std::pow(10.0, spl_dba / 10.0);
    }
    
    // 3. Широкосмуговий шум сходу з задньої кромки (BPM)
    const double u_eff = 0.75 * report.tip_speed_mps;
    const double delta_star = 0.003 * spec.chord_m;
    report.broadband_peak_hz = 0.10 * u_eff / delta_star;
    
    const double p_bb = std::max(1e-12, 1.2e-5 * (kRhoAir * std::pow(u_eff, 2.5) * 
                                 std::sqrt(delta_star * radius) / (kSoundSpeed * spec.distance_m)));
    report.broadband_spl_db = 20.0 * std::log10(p_bb / kPref);
    
    linear_energy_sum += std::pow(10.0, report.broadband_spl_db / 10.0);
    const double bb_dba = report.broadband_spl_db + calculate_a_weighting(report.broadband_peak_hz);
    a_weighted_energy_sum += std::pow(10.0, bb_dba / 10.0);
    
    report.total_spl_db = 10.0 * std::log10(linear_energy_sum);
    report.total_spl_dba = 10.0 * std::log10(a_weighted_energy_sum);
    
    return report;
}

} // namespace aeroacoustics

int main() {
    using namespace aeroacoustics;
    
    PropellerSpec drone_prop{
        .diameter_m = 0.254,     // 10 дюймів
        .num_blades = 2,
        .rpm = 6000.0,
        .thrust_n = 7.5,         // 7.5 Н тяги
        .power_w = 85.0,
        .chord_m = 0.022,
        .thickness_m = 0.0025,
        .distance_m = 10.0,
        .directivity_angle_deg = 110.0
    };
    
    const auto report = evaluate_propeller_noise(drone_prop);
    
    std::cout << "=== Аероакустичний розрахунок гвинта дрона (C++20) ===\n"
              << std::fixed << std::setprecision(1)
              << "Діаметр: " << drone_prop.diameter_m * 1000.0 << " мм | Лопатей: " 
              << drone_prop.num_blades << " | Оберти: " << drone_prop.rpm << " RPM\n"
              << "Швидкість кінчиків: " << report.tip_speed_mps << " м/с (M_tip = " 
              << std::setprecision(3) << report.tip_mach << ")\n"
              << std::setprecision(1)
              << "Лопатева частота (BPF): " << report.bpf_hz << " Гц\n\n"
              << "Тональний спектр (Гутін + Демінг):\n";
              
    for (const auto& h : report.harmonics) {
        std::cout << "  Гармоніка " << h.index << " (" << std::setw(6) << h.frequency_hz 
                  << " Гц): " << std::setw(5) << h.spl_db << " дБ | " 
                  << std::setw(5) << h.spl_dba << " дБА\n";
    }
    
    std::cout << "\nШирокосмуговий шум (схід з кромки BPM):\n"
              << "  Пікова частота: " << report.broadband_peak_hz << " Гц | Рівень: " 
              << report.broadband_spl_db << " дБ\n"
              << "\nПідсумковий рівень шуму на відстані " << drone_prop.distance_m << " м:\n"
              << "  Сумарний SPL:  " << report.total_spl_db << " дБ (лінійний)\n"
              << "  Сумарний SPL:  " << report.total_spl_dba << " дБА (A-зважений)\n";
              
    return 0;
}
