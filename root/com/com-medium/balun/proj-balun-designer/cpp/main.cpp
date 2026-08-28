#include <iostream>
#include <cmath>
#include <numbers>
#include <format>
#include <expected>
#include <string_view>

struct BalunInput {
    double freq_mhz{14.150};
    double z0_ohm{50.0};
    double target_zcm_ohm{1000.0};
    double power_watts{500.0};
    double core_al_nh{240.0};
    double core_ae_cm2{1.58};
};

struct BalunOutput {
    double min_l_uh{0.0};
    int turns_count{0};
    double actual_zcm_ohm{0.0};
    double cmrr_db{0.0};
    double v_peak{0.0};
    double b_peak_gauss{0.0};
    bool is_saturated{false};
};

enum class BalunCalcError {
    InvalidFrequency,
    InvalidImpedance,
    InvalidCoreData
};

[[nodiscard]] std::expected<BalunOutput, BalunCalcError> calculate_balun(const BalunInput& in) noexcept {
    if (in.freq_mhz <= 0.0) return std::unexpected(BalunCalcError::InvalidFrequency);
    if (in.z0_ohm <= 0.0 || in.target_zcm_ohm <= 0.0) return std::unexpected(BalunCalcError::InvalidImpedance);

    BalunOutput out;
    const double omega = 2.0 * std::numbers::pi * (in.freq_mhz * 1e6);

    // 1. Необхідна індуктивність L_cm
    const double req_l_h = in.target_zcm_ohm / omega;
    out.min_l_uh = req_l_h * 1e6;

    // 2. Кількість витків N
    const double req_l_nh = req_l_h * 1e9;
    if (in.core_al_nh > 0.0) {
        out.turns_count = static_cast<int>(std::ceil(std::sqrt(req_l_nh / in.core_al_nh)));
        out.turns_count = std::max(1, out.turns_count);
    }

    // 3. Фактичний опір та CMRR
    const double actual_l_nh = static_cast<double>(out.turns_count * out.turns_count) * in.core_al_nh;
    const double actual_l_h = actual_l_nh * 1e-9;
    out.actual_zcm_ohm = omega * actual_l_h;

    out.cmrr_db = 20.0 * std::log10(1.0 + (out.actual_zcm_ohm / (2.0 * in.z0_ohm)));

    // 4. Напруга та магнітна індукція
    out.v_peak = std::sqrt(2.0 * in.power_watts * in.z0_ohm);

    if (in.core_ae_cm2 > 0.0 && out.turns_count > 0) {
        const double f_hz = in.freq_mhz * 1e6;
        out.b_peak_gauss = (out.v_peak * 1e8) / (4.44 * f_hz * in.core_ae_cm2 * static_cast<double>(out.turns_count));
    }

    out.is_saturated = (out.b_peak_gauss > 2500.0);

    return out;
}

int main() {
    constexpr BalunInput input{
        .freq_mhz = 14.150,
        .z0_ohm = 50.0,
        .target_zcm_ohm = 1000.0,
        .power_watts = 500.0,
        .core_al_nh = 240.0,
        .core_ae_cm2 = 1.58
    };

    const auto result = calculate_balun(input);

    if (!result) {
        std::cerr << "Помилка обчислення параметрів балуна!\n";
        return 1;
    }

    const auto& out = *result;

    std::cout << std::format("=== РОЗРАХУНОК СТРУМОВОГО БАЛУНА ГУАНЕЛЛА (C++) ===\n");
    std::cout << std::format("Частота            : {:.3f} МГц\n", input.freq_mhz);
    std::cout << std::format("Потужність         : {:.1f} Вт\n", input.power_watts);
    std::cout << std::format("Мін. індуктивність : {:.2f} мкГн\n", out.min_l_uh);
    std::cout << std::format("Кількість витків N : {} витків\n", out.turns_count);
    std::cout << std::format("Фактичний Z_cm     : {:.1f} Ом\n", out.actual_zcm_ohm);
    std::cout << std::format("Пригнічення CMRR   : {:.2f} дБ\n", out.cmrr_db);
    std::cout << std::format("Пікова ВЧ напруга  : {:.1f} В\n", out.v_peak);
    std::cout << std::format("Магнітна індукція  : {:.1f} Гаусс\n", out.b_peak_gauss);
    std::cout << std::format("Статус осердя      : {}\n", 
        out.is_saturated ? "УВАГА: Ризик насичення!" : "ОК (Безпечний режим)");

    return 0;
}
