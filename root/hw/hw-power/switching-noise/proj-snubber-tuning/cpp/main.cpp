#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>

struct SnubberInput {
    double f1_mhz{0.0};       // Початкова частота дзвіну (МГц)
    double f2_mhz{0.0};       // Частота з тестовою ємністю (МГц)
    double c_add_pf{0.0};     // Тестова калібрувальна ємність (пФ)
    double vin_volts{0.0};    // Вхідна напруга живлення (В)
    double fsw_khz{0.0};      // Частота комутації перетворювача (кГц)
    double kc_factor{3.0};    // Кратність ємності снубера (2.0 - 4.0)
    double l_post_uh{0.0};    // Індуктивність вторинного фільтра (мкГн)
    double c_post_uf{0.0};    // Ємність вторинного фільтра (мкФ)
};

struct SnubberResult {
    double c_par_pf{0.0};
    double l_par_nh{0.0};
    double z0_ohms{0.0};
    double c_snub_pf{0.0};
    double r_snub_ohms{0.0};
    double p_snub_mw{0.0};
    double fc_post_khz{0.0};
    double att_100mhz_db{0.0};
};

enum class CalculationError {
    InvalidFrequencies,
    InvalidTestCapacitor,
    FrequencyDidNotDrop
};

[[nodiscard]] constexpr std::string_view error_message(CalculationError err) noexcept {
    switch (err) {
        case CalculationError::InvalidFrequencies:
            return "Частоти мають бути строго додатними числами.";
        case CalculationError::InvalidTestCapacitor:
            return "Тестова ємність має бути більшою за нуль.";
        case CalculationError::FrequencyDidNotDrop:
            return "Частота f2 із додатковою ємністю повинна бути меншою за f1.";
    }
    return "Невідома помилка обчислення.";
}

[[nodiscard]] std::expected<SnubberResult, CalculationError> calculate_snubber(const SnubberInput& in) noexcept {
    if (in.f1_mhz <= 0.0 || in.f2_mhz <= 0.0) {
        return std::unexpected(CalculationError::InvalidFrequencies);
    }
    if (in.c_add_pf <= 0.0) {
        return std::unexpected(CalculationError::InvalidTestCapacitor);
    }
    if (in.f2_mhz >= in.f1_mhz) {
        return std::unexpected(CalculationError::FrequencyDidNotDrop);
    }

    SnubberResult res;
    const double ratio = in.f1_mhz / in.f2_mhz;
    const double ratio_sq = ratio * ratio;

    // C_par = C_add / ((f1/f2)^2 - 1)
    res.c_par_pf = in.c_add_pf / (ratio_sq - 1.0);

    // L_par = 1 / (4 * pi^2 * f1^2 * C_par)
    const double f1_hz = in.f1_mhz * 1.0e6;
    const double c_par_farads = res.c_par_pf * 1.0e-12;
    const double pi = std::numbers::pi;
    const double l_par_henry = 1.0 / (4.0 * pi * pi * f1_hz * f1_hz * c_par_farads);
    res.l_par_nh = l_par_henry * 1.0e9;

    // Z_0 = sqrt(L_par / C_par)
    res.z0_ohms = std::sqrt(l_par_henry / c_par_farads);

    // Параметри RC-снубера
    const double kc = (in.kc_factor >= 1.0) ? in.kc_factor : 3.0;
    res.c_snub_pf = kc * res.c_par_pf;

    const double c_total_farads = (res.c_par_pf + res.c_snub_pf) * 1.0e-12;
    res.r_snub_ohms = std::sqrt(l_par_henry / c_total_farads);

    // Теплові втрати: P = C_snub * Vin^2 * f_sw
    const double fsw_hz = in.fsw_khz * 1.0e3;
    const double c_snub_farads = res.c_snub_pf * 1.0e-12;
    res.p_snub_mw = c_snub_farads * (in.vin_volts * in.vin_volts) * fsw_hz * 1.0e3;

    // Вторинний фільтр
    if (in.l_post_uh > 0.0 && in.c_post_uf > 0.0) {
        const double l_post_h = in.l_post_uh * 1.0e-6;
        const double c_post_f = in.c_post_uf * 1.0e-6;
        const double fc_hz = 1.0 / (2.0 * pi * std::sqrt(l_post_h * c_post_f));
        res.fc_post_khz = fc_hz * 1.0e-3;

        constexpr double target_f_hz = 100.0e6;
        if (target_f_hz > fc_hz) {
            res.att_100mhz_db = 40.0 * std::log10(target_f_hz / fc_hz);
        }
    }

    return res;
}

int main() {
    constexpr SnubberInput input{
        .f1_mhz = 180.0,
        .f2_mhz = 95.0,
        .c_add_pf = 470.0,
        .vin_volts = 24.0,
        .fsw_khz = 500.0,
        .kc_factor = 3.0,
        .l_post_uh = 0.47,
        .c_post_uf = 10.0
    };

    const auto result = calculate_snubber(input);
    if (!result) {
        std::cerr << "Помилка: " << error_message(result.error()) << '\n';
        return 1;
    }

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== РЕЗУЛЬТАТИ РОЗРАХУНКУ ДЕМПФЕРА (C++) ===\n";
    std::cout << "Паразитна ємність вузла C_par:       " << result->c_par_pf << " пФ\n";
    std::cout << "Паразитна індуктивність L_par:       " << result->l_par_nh << " нГн\n";
    std::cout << "Характеристичний опір контуру Z_0:   " << result->z0_ohms << " Ом\n\n";

    std::cout << "Рекомендована ємність снубера C_sn:  " << result->c_snub_pf << " пФ (C0G/NP0)\n";
    std::cout << "Рекомендований опір снубера R_sn:    " << result->r_snub_ohms << " Ом (SMD)\n";
    std::cout << "Потужність розсіювання на R_sn:      " << result->p_snub_mw << " мВт (0805/1206)\n\n";

    if (result->fc_post_khz > 0.0) {
        std::cout << "=== ВТОРИННИЙ LC-ФІЛЬТР ===\n";
        std::cout << "Частота зрізу f_c:                   " << result->fc_post_khz << " кГц\n";
        std::cout << "Придушення на 100 МГц:               " << result->att_100mhz_db << " дБ\n";
    }

    return 0;
}
