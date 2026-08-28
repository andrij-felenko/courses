#include <iostream>
#include <cmath>
#include <numbers>
#include <optional>
#include <string_view>

struct FiberParams {
    double n1{1.4677};          // Показник заломлення серцевини
    double n2{1.4624};          // Показник заломлення оболонки
    double core_radius_m{4.1e-6};// Радіус серцевини (м)
    double alpha_dB_km{0.35};   // Коефіцієнт згасання (дБ/км)
};

struct FiberAnalysis {
    double na;                  // Числова апертура NA
    double acceptance_angle_deg;// Кут вводу в повітрі
    double v_number;            // Нормована частота V
    bool is_single_mode;        // Прапорець одномодового режиму
    std::size_t mode_count;     // Оцінка кількості мод
    double cutoff_wavelength_nm;// Довжина хвилі відсічки
};

struct LinkBudgetInput {
    double length_km{10.0};
    int splice_count{2};
    double splice_loss_dB{0.05};
    int connector_count{2};
    double conn_loss_dB{0.30};
    double tx_power_dBm{0.0};
    double rx_sens_dBm{-30.0};
};

struct LinkBudgetResult {
    double total_attenuation_dB;
    double power_margin_dB;
    bool is_link_viable;
};

class FiberCalculator {
public:
    static std::optional<FiberAnalysis> analyze(const FiberParams& fiber, double wavelength_nm) noexcept {
        if (fiber.n1 <= fiber.n2 || fiber.core_radius_m <= 0.0 || wavelength_nm <= 0.0) {
            return std::nullopt;
        }

        const double na = std::sqrt(fiber.n1 * fiber.n1 - fiber.n2 * fiber.n2);
        const double sin_theta = std::min(1.0, na);
        const double acceptance_angle = std::asin(sin_theta) * (180.0 / std::numbers::pi);

        const double wavelength_m = wavelength_nm * 1e-9;
        const double v_num = (2.0 * std::numbers::pi * fiber.core_radius_m / wavelength_m) * na;
        const bool single_mode = (v_num < 2.405);

        const std::size_t modes = single_mode ? 1 : static_cast<std::size_t>(std::round((v_num * v_num) / 2.0));
        const double cutoff_nm = ((2.0 * std::numbers::pi * fiber.core_radius_m * na) / 2.405) * 1e9;

        return FiberAnalysis{
            .na = na,
            .acceptance_angle_deg = acceptance_angle,
            .v_number = v_num,
            .is_single_mode = single_mode,
            .mode_count = modes,
            .cutoff_wavelength_nm = cutoff_nm
        };
    }

    static std::optional<LinkBudgetResult> calculateLink(const FiberParams& fiber, const LinkBudgetInput& link) noexcept {
        if (link.length_km < 0.0) return std::nullopt;

        const double fiber_loss = link.length_km * fiber.alpha_dB_km;
        const double splices_loss = link.splice_count * link.splice_loss_dB;
        const double conns_loss = link.connector_count * link.conn_loss_dB;

        const double total_loss = fiber_loss + splices_loss + conns_loss;
        const double available_power = link.tx_power_dBm - link.rx_sens_dBm;
        const double margin = available_power - total_loss;

        return LinkBudgetResult{
            .total_attenuation_dB = total_loss,
            .power_margin_dB = margin,
            .is_link_viable = (margin >= 3.0)
        };
    }
};

int main() {
    constexpr FiberParams smf28{
        .n1 = 1.4677,
        .n2 = 1.4624,
        .core_radius_m = 4.1e-6,
        .alpha_dB_km = 0.35
    };

    if (auto res = FiberCalculator::analyze(smf28, 1310.0)) {
        std::cout << "--- Аналіз волокна SMF-28 (C++) ---\n"
                  << "Числова апертура (NA): " << res->na << "\n"
                  << "Апертурний кут:        " << res->acceptance_angle_deg << " deg\n"
                  << "Параметр V:           " << res->v_number 
                  << (res->is_single_mode ? " (Одномодове)" : " (Багатомодове)") << "\n"
                  << "Відсічка λc:          " << res->cutoff_wavelength_nm << " nm\n\n";
    }

    constexpr LinkBudgetInput link{
        .length_km = 40.0,
        .splice_count = 8,
        .splice_loss_dB = 0.05,
        .connector_count = 4,
        .conn_loss_dB = 0.30,
        .tx_power_dBm = 0.0,
        .rx_sens_dBm = -30.0
    };

    if (auto budget = FiberCalculator::calculateLink(smf28, link)) {
        std::cout << "--- Бюджет оптичної траси (C++) ---\n"
                  << "Загальні втрати: " << budget->total_attenuation_dB << " dB\n"
                  << "Запас потужності: " << budget->power_margin_dB << " dB\n"
                  << "Статус лінії:     " << (budget->is_link_viable ? "ПРОЙШЛА (OK)" : "НЕВДАЧА") << "\n";
    }

    return 0;
}
