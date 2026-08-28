#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <format>
#include <string_view>

namespace rf::antenna {

struct GammaInput {
    double freq_mhz{144.2};
    double target_z0{50.0};
    double r_ant{18.0};
    double r_element_mm{6.0};
    double r_rod_mm{2.0};
    double spacing_mm{45.0};
};

struct GammaResult {
    double u_ratio;
    double step_up_m;
    double z0_loop;
    double x_loop;
    double gamma_len_cm;
    double c_gamma_pf;
    double balun_l_uh;
};

enum class CalculateError {
    InvalidInputParameters,
    TransformationRatioTooLow
};

[[nodiscard]] constexpr std::string_view error_to_string(CalculateError err) noexcept {
    switch (err) {
        case CalculateError::InvalidInputParameters:
            return "Некоректні геометричні параметри: радіуси або відстань за межами фізичної норми.";
        case CalculateError::TransformationRatioTooLow:
            return "Коефіцієнт m занадто малий: трансформований опір нижчий за 50 Ом. Збільште відстань S або зменшіть r_rod.";
    }
    return "Невідома помилка.";
}

class GammaCalculator {
public:
    [[nodiscard]] static std::expected<GammaResult, CalculateError> 
    compute(const GammaInput& in) noexcept {
        if (in.freq_mhz <= 0.0 || in.r_ant <= 0.0 || 
            in.r_element_mm <= 0.0 || in.r_rod_mm <= 0.0 || 
            in.spacing_mm <= (in.r_element_mm + in.r_rod_mm)) {
            return std::unexpected(CalculateError::InvalidInputParameters);
        }

        constexpr double c_speed = 299'792'458.0; // Швидкість світла м/с
        const double lambda_m = c_speed / (in.freq_mhz * 1e6);

        // 1. Обчислення коефіцієнта u та автотрансформатора m
        const double u = std::log(in.spacing_mm / in.r_rod_mm) / std::log(in.spacing_mm / in.r_element_mm);
        const double m = (1.0 + u) * (1.0 + u);

        const double r_transformed = m * in.r_ant;
        if (r_transformed < in.target_z0) {
            return std::unexpected(CalculateError::TransformationRatioTooLow);
        }

        // 2. Хвильовий опір двопровідного шлейфу Z0_loop
        const double z0_loop = 120.0 * std::log(in.spacing_mm / std::sqrt(in.r_element_mm * in.r_rod_mm));

        // 3. Реактивна індуктивність шлейфу X_loop
        const double ratio = r_transformed / in.target_z0;
        const double x_loop = r_transformed * std::sqrt(ratio - 1.0);

        // 4. Довжина гама-стрижня L_γ
        const double beta_l = std::atan(x_loop / z0_loop);
        const double l_gamma_m = (beta_l * lambda_m) / (2.0 * std::numbers::pi);

        // 5. Компенсаційний конденсатор C_γ
        const double omega = 2.0 * std::numbers::pi * in.freq_mhz * 1e6;
        const double c_gamma_pf = (1.0 / (omega * x_loop)) * 1e12;

        // 6. Мінімальна індуктивність дроселя балуна
        constexpr double target_z_cm = 500.0;
        const double balun_l_uh = (target_z_cm / omega) * 1e6;

        return GammaResult{
            .u_ratio = u,
            .step_up_m = m,
            .z0_loop = z0_loop,
            .x_loop = x_loop,
            .gamma_len_cm = l_gamma_m * 100.0,
            .c_gamma_pf = c_gamma_pf,
            .balun_l_uh = balun_l_uh
        };
    }
};

} // namespace rf::antenna

int main() {
    using namespace rf::antenna;

    const GammaInput input{
        .freq_mhz = 144.2,
        .target_z0 = 50.0,
        .r_ant = 18.0,
        .r_element_mm = 6.0,
        .r_rod_mm = 2.0,
        .spacing_mm = 45.0
    };

    std::cout << "=== Інженерний калькулятор гама-узгоджувача (C++23 Modern Implementation) ===\n";

    const auto res = GammaCalculator::compute(input);

    if (res.has_value()) {
        const auto& out = res.value();
        std::cout << std::format("Частота: {:.2f} МГц\n", input.freq_mhz);
        std::cout << std::format("Коефіцієнт u: {:.3f} | Автотрансформатор m: {:.3f}\n", 
                                 out.u_ratio, out.step_up_m);
        std::cout << std::format("Хвильовий опір шлейфу Z0g: {:.1f} Ом\n", out.z0_loop);
        std::cout << "---------------------------------------------------\n";
        std::cout << std::format("Довжина гама-стрижня L_γ: {:.2f} см\n", out.gamma_len_cm);
        std::cout << std::format("Ємність конденсатора C_γ : {:.2f} пФ\n", out.c_gamma_pf);
        std::cout << std::format("Індуктивність балуна L  : {:.3f} мкГн (Z_cm >= 500 Ом)\n", out.balun_l_uh);
    } else {
        std::cerr << std::format("Помилка розрахунку: {}\n", error_to_string(res.error()));
    }

    return 0;
}
