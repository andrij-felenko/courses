#include <iostream>
#include <iomanip>
#include <cmath>
#include <string_view>
#include <numbers>
#include <span>
#include <algorithm>

namespace acoustics {

// Фізичні константи середовища
inline constexpr float AIR_DENSITY       = 1.204f;     // кг/м³ (@ 20°C)
inline constexpr float AIR_SPEED_SOUND   = 343.0f;     // м/с
inline constexpr float FR4_DENSITY       = 1850.0f;    // кг/м³
inline constexpr float FR4_YOUNG_MODULUS = 22.0e9f;    // Па
inline constexpr float FR4_POISSON_RATIO = 0.14f;
inline constexpr float P_REF_ACOUSTIC    = 20.0e-6f;   // 20 мкПа (поріг чутності)

// Параметри кераміки BaTiO3 класу X7R
inline constexpr float X7R_D33_ZERO      = 200.0e-12f; // м/В
inline constexpr float X7R_M33_ELECTRO   = 2.0e-16f;   // м²/В²
inline constexpr float X7R_POISSON_RATIO = 0.30f;

struct MlccParams {
    float length_m        = 0.0032f;  // Довжина корпусу (1206: 3.2 мм)
    float width_m         = 0.0016f;  // Ширина корпусу
    float height_m        = 0.0016f;  // Висота корпусу
    float layer_thick_m   = 2.0e-6f;  // Товщина шару діелектрика
    float v_dc            = 12.0f;    // Напруга постійного зміщення, В
    float v_ripple_pk     = 1.0f;     // Амплітуда змінних пульсацій (пік), В
    float f_ripple_hz     = 3450.0f;  // Частота пульсацій, Гц
};

struct PcbParams {
    float length_m    = 0.12f;    // Довжина плати, м (120 мм)
    float width_m     = 0.08f;    // Ширина плати, м (80 мм)
    float thickness_m = 0.0016f;  // Товщина текстоліту (1.6 мм)
    float q_factor    = 25.0f;    // Механічна добротність FR4
    float dist_m      = 0.5f;     // Відстань вимірювання (0.5 м)
};

enum class RiskLevel {
    Inaudible,
    Moderate,
    High,
    Critical
};

struct AcousticReport {
    float d_eff_pm_v;
    float delta_l_nm;
    float f_closest_mode_hz;
    float q_amplification;
    float spl_db;
    float spl_dba;
    RiskLevel risk;

    [[nodiscard]] std::string_view risk_string() const noexcept {
        switch (risk) {
            case RiskLevel::Inaudible: return "НЕЧУТНО (Безпечно)";
            case RiskLevel::Moderate:  return "ПОМІРНИЙ (Чутно в тихій кімнаті)";
            case RiskLevel::High:      return "ВИСОКИЙ (Дратівливий тональний писк)";
            case RiskLevel::Critical:  return "КРИТИЧНИЙ (Нестерпний гучний свист)";
        }
        return "Невідомо";
    }
};

// Розрахунок A-зважування за стандартом IEC 61672-1
[[nodiscard]] constexpr float calculate_a_weighting(float f_hz) noexcept {
    float f = (f_hz < 10.0f) ? 10.0f : f_hz;
    float f2 = f * f;
    float num = 12194.0f * 12194.0f * f2 * f2;
    float den = (f2 + 20.6f * 20.6f) *
                std::sqrt((f2 + 107.7f * 107.7f) * (f2 + 737.9f * 737.9f)) *
                (f2 + 12194.0f * 12194.0f);
    if (den <= 0.0f) return 0.0f;
    return 20.0f * std::log10(num / den) + 2.0f;
}

[[nodiscard]] AcousticReport evaluate_acoustics(const MlccParams& cap, const PcbParams& pcb) noexcept {
    // 1. Електромеханічний розрахунок кераміки BaTiO3
    const float e_dc = cap.v_dc / cap.layer_thick_m;
    const float e_ac = cap.v_ripple_pk / cap.layer_thick_m;
    const float d_eff = X7R_D33_ZERO + 2.0f * X7R_M33_ELECTRO * e_dc;
    const float strain_x = X7R_POISSON_RATIO * d_eff * e_ac;
    const float delta_l = strain_x * cap.length_m;

    // 2. Механічні параметри пластини FR4
    const float t3 = pcb.thickness_m * pcb.thickness_m * pcb.thickness_m;
    const float d_rigidity = (FR4_YOUNG_MODULUS * t3) /
                             (12.0f * (1.0f - FR4_POISSON_RATIO * FR4_POISSON_RATIO));
    const float m_surface = FR4_DENSITY * pcb.thickness_m;
    const float c_plate = std::sqrt(d_rigidity / m_surface);

    // 3. Пошук найближчої власної згинальної моди плати
    float min_diff = 1.0e9f;
    float closest_mode = 0.0f;

    for (int m = 1; m <= 6; ++m) {
        for (int n = 1; n <= 6; ++n) {
            float term_m = static_cast<float>(m) / pcb.length_m;
            float term_n = static_cast<float>(n) / pcb.width_m;
            float f_mn = (std::numbers::pi_v<float> / 2.0f) * c_plate *
                         (term_m * term_m + term_n * term_n);
            float diff = std::abs(f_mn - cap.f_ripple_hz);
            if (diff < min_diff) {
                min_diff = diff;
                closest_mode = f_mn;
            }
        }
    }

    // Резонансний фактор підсилення
    const float f_ratio = cap.f_ripple_hz / closest_mode;
    const float denom = std::sqrt(std::pow(1.0f - f_ratio * f_ratio, 2.0f) +
                                  std::pow(f_ratio / pcb.q_factor, 2.0f));
    const float q_amp = std::min((denom > 0.001f) ? (1.0f / denom) : pcb.q_factor,
                                 pcb.q_factor);

    // 4. Динамічний прогин та швидкість вібрації поверхні
    const float static_w0 = delta_l * (pcb.thickness_m / (2.0f * cap.length_m));
    const float w_pk = static_w0 * q_amp;
    const float omega = 2.0f * std::numbers::pi_v<float> * cap.f_ripple_hz;
    const float v_rms = (omega * w_pk) / std::sqrt(2.0f);

    // 5. Акустичне випромінювання та звуковий тиск
    const float f_crit = (AIR_SPEED_SOUND * AIR_SPEED_SOUND / (2.0f * std::numbers::pi_v<float>)) *
                         std::sqrt(m_surface / d_rigidity);
    const float sigma_rad = (cap.f_ripple_hz < f_crit) ?
                            std::max(0.20f * (cap.f_ripple_hz / f_crit), 0.02f) : 1.0f;

    const float pcb_area = pcb.length_m * pcb.width_m;
    const float z_air = AIR_DENSITY * AIR_SPEED_SOUND;
    const float w_acoustic = sigma_rad * z_air * pcb_area * (v_rms * v_rms);

    const float intensity = (w_acoustic * 2.0f) /
                            (4.0f * std::numbers::pi_v<float> * pcb.dist_m * pcb.dist_m);
    const float p_rms = std::sqrt(std::max(intensity * z_air, 1.0e-18f));

    const float spl_db = 20.0f * std::log10(p_rms / P_REF_ACOUSTIC);
    const float spl_dba = spl_db + calculate_a_weighting(cap.f_ripple_hz);

    RiskLevel risk;
    if (spl_dba < 25.0f) risk = RiskLevel::Inaudible;
    else if (spl_dba < 38.0f) risk = RiskLevel::Moderate;
    else if (spl_dba < 52.0f) risk = RiskLevel::High;
    else risk = RiskLevel::Critical;

    return {
        .d_eff_pm_v = d_eff * 1.0e12f,
        .delta_l_nm = delta_l * 1.0e9f,
        .f_closest_mode_hz = closest_mode,
        .q_amplification = q_amp,
        .spl_db = spl_db,
        .spl_dba = spl_dba,
        .risk = risk
    };
}

} // namespace acoustics

int main() {
    constexpr acoustics::MlccParams cap{
        .length_m = 0.0032f,      // 1206
        .width_m = 0.0016f,
        .height_m = 0.0016f,
        .layer_thick_m = 2.0e-6f,
        .v_dc = 12.0f,
        .v_ripple_pk = 1.0f,
        .f_ripple_hz = 3450.0f    // 3.45 кГц
    };

    constexpr acoustics::PcbParams pcb{
        .length_m = 0.12f,
        .width_m = 0.08f,
        .thickness_m = 0.0016f,
        .q_factor = 25.0f,
        .dist_m = 0.5f
    };

    const auto report = acoustics::evaluate_acoustics(cap, pcb);

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "=====================================================\n";
    std::cout << "   АНАЛІЗ АКУСТИЧНОГО ШУМУ КЕРАМІЧНОГО КОНДЕНСАТОРА   \n";
    std::cout << "=====================================================\n";
    std::cout << "Ефективний п'єзомодуль d_eff : " << report.d_eff_pm_v << " пм/В\n";
    std::cout << "Амплітуда коливань корпусу dL: " << std::setprecision(2) << report.delta_l_nm << " нм\n";
    std::cout << "Найближча резонансна мода PCB: " << std::setprecision(1) << report.f_closest_mode_hz << " Гц\n";
    std::cout << "Фактор підсилення резонансу Q: " << std::setprecision(2) << report.q_amplification << " x\n";
    std::cout << "Рівень звукового тиску SPL   : " << std::setprecision(1) << report.spl_db << " дБ (лінійний)\n";
    std::cout << "Рівень звукового тиску dBA   : " << report.spl_dba << " дБА (A-зважений)\n";
    std::cout << "Категорія акустичного ризику : " << report.risk_string() << "\n";
    std::cout << "=====================================================\n";

    return 0;
}
