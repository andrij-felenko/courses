#include <cmath>
#include <iostream>

struct OpAmpOffsetSpecs {
    double vos_base_uv{0.0};    // Початковий зсув за 25°C (мкВ)
    double drift_uv_per_c{0.0}; // Температурний дрейф (мкВ/°C)
    double cmrr_db{0.0};        // CMRR (дБ)
    double psrr_db{0.0};        // PSRR (дБ)
};

struct OffsetBudgetResult {
    double worst_case_uv{0.0};  // Найгірша адитивна похибка (мкВ)
    double rss_uv{0.0};         // Статистична середньоквадратична похибка (мкВ)
};

// Розрахунок сумарної напруги зсуву, зведеної до входу
[[nodiscard]] constexpr OffsetBudgetResult calculate_offset_budget(
    const OpAmpOffsetSpecs& specs,
    double delta_t_c,
    double delta_vcm_v,
    double delta_vsupply_v) noexcept {
    
    const double temp_error_uv = specs.drift_uv_per_c * std::abs(delta_t_c);

    const double cmrr_ratio = std::pow(10.0, specs.cmrr_db / 20.0);
    const double psrr_ratio = std::pow(10.0, specs.psrr_db / 20.0);

    const double cmrr_error_uv = (std::abs(delta_vcm_v) / cmrr_ratio) * 1.0e6;
    const double psrr_error_uv = (std::abs(delta_vsupply_v) / psrr_ratio) * 1.0e6;

    const double worst_case = specs.vos_base_uv + temp_error_uv + cmrr_error_uv + psrr_error_uv;

    const double rss = std::sqrt(specs.vos_base_uv * specs.vos_base_uv +
                                 temp_error_uv * temp_error_uv +
                                 cmrr_error_uv * cmrr_error_uv +
                                 psrr_error_uv * psrr_error_uv);

    return {worst_case, rss};
}
