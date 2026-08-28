// loading_coil_calc.cpp - Обчислення завантажувальної котушки мовою C++
#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <expected>
#include <string>

struct AntennaInputs {
    double freq_mhz{7.10};
    double height_m{1.80};
    double wire_radius_mm{2.0};
    double ground_loss_ohm{4.0};
    double coil_q{200.0};
    double power_watts{100.0};
    double coil_diam_cm{5.0};
    double coil_len_cm{8.0};
};

struct AntennaResults {
    double wavelength_m;
    double c_ant_pf;
    double x_c_ohm;
    double l_coil_uh;
    double r_rad_ohm;
    double r_coil_ohm;
    double r_total_ohm;
    double efficiency_pct;
    double q_ant;
    double bandwidth_khz;
    double v_peak_volts;
    double p_heat_watts;
    int turns_count;
};

enum class CalcError {
    InvalidParameters,
    GeometryDegeneracy
};

class LoadingCoilCalculator {
public:
    [[nodiscard]] static std::expected<AntennaResults, CalcError> calculate(const AntennaInputs& in) noexcept {
        if (in.freq_mhz <= 0.0 || in.height_m <= 0.0 || in.wire_radius_mm <= 0.0 || in.coil_q <= 0.0) {
            return std::unexpected(CalcError::InvalidParameters);
        }

        constexpr double c_speed = 299792458.0;
        constexpr double eps0 = 8.854187817e-12;
        constexpr double pi = std::numbers::pi;

        const double freq_hz = in.freq_mhz * 1.0e6;
        const double omega = 2.0 * pi * freq_hz;
        const double wavelength = c_speed / freq_hz;

        const double wire_radius_m = in.wire_radius_mm / 1000.0;
        const double ln_ratio = std::log(in.height_m / wire_radius_m) - 1.0;
        if (ln_ratio <= 0.2) {
            return std::unexpected(CalcError::GeometryDegeneracy);
        }

        const double c_farads = (2.0 * pi * eps0 * in.height_m) / ln_ratio;
        const double c_ant_pf = c_farads * 1.0e12;
        const double x_c = 1.0 / (omega * c_farads);
        const double l_coil_uh = (x_c / omega) * 1.0e6;

        const double h_lambda = in.height_m / wavelength;
        const double r_rad = 160.0 * pi * pi * h_lambda * h_lambda;
        const double r_coil = x_c / in.coil_q;
        const double r_total = r_rad + in.ground_loss_ohm + r_coil;

        const double eff_pct = (r_rad / r_total) * 100.0;
        const double q_ant = x_c / r_total;
        const double bw_khz = (in.freq_mhz * 1000.0) / q_ant;

        const double i_ant_rms = std::sqrt(in.power_watts / r_total);
        const double v_rms = i_ant_rms * x_c;
        const double v_peak = v_rms * std::numbers::sqrt2;
        const double p_heat = i_ant_rms * i_ant_rms * r_coil;

        int turns = 0;
        if (in.coil_diam_cm > 0.0 && in.coil_len_cm > 0.0) {
            const double d = in.coil_diam_cm;
            const double l = in.coil_len_cm;
            const double n_sq = (l_coil_uh * (45.0 * d + 100.0 * l)) / (2.54 * d * d);
            turns = static_cast<int>(std::ceil(std::sqrt(n_sq)));
        }

        return AntennaResults{
            .wavelength_m = wavelength,
            .c_ant_pf = c_ant_pf,
            .x_c_ohm = x_c,
            .l_coil_uh = l_coil_uh,
            .r_rad_ohm = r_rad,
            .r_coil_ohm = r_coil,
            .r_total_ohm = r_total,
            .efficiency_pct = eff_pct,
            .q_ant = q_ant,
            .bandwidth_khz = bw_khz,
            .v_peak_volts = v_peak,
            .p_heat_watts = p_heat,
            .turns_count = turns
        };
    }
};

void print_cpp_report(const AntennaInputs& in, const AntennaResults& res) {
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "========================================================\n";
    std::cout << "  РЕЗУЛЬТАТИ РОЗРАХУНКУ ЗАВАНТАЖУВАЛЬНОЇ КОТУШКИ (C++)  \n";
    std::cout << "========================================================\n";
    std::cout << "Вхідні параметри:\n";
    std::cout << "  Частота: " << in.freq_mhz << " МГц (λ = " << res.wavelength_m << " м)\n";
    std::cout << "  Висота штиря h: " << in.height_m << " м (" 
              << (in.height_m / res.wavelength_m) * 100.0 << "% λ)\n";
    std::cout << "  Радіус провідника: " << in.wire_radius_mm << " мм\n";
    std::cout << "  Потужність передавача: " << std::setprecision(0) << in.power_watts << " Вт\n";
    std::cout << std::setprecision(2);
    std::cout << "--------------------------------------------------------\n";
    std::cout << "Параметри котушки та імпедансу:\n";
    std::cout << "  Ємність штиря C_ant: " << res.c_ant_pf << " пФ\n";
    std::cout << "  Реактивний опір X_C: -j" << res.x_c_ohm << " Ом\n";
    std::cout << "  Необхідна індуктивність L_coil: " << res.l_coil_uh << " мкГн\n";
    std::cout << "  Каркас D=" << in.coil_diam_cm << " см, довжина l=" << in.coil_len_cm 
              << " см  ⇒  " << res.turns_count << " витків\n";
    std::cout << "--------------------------------------------------------\n";
    std::cout << "Баланс опорів та ККД:\n";
    std::cout << "  Опір випромінювання R_рад: " << res.r_rad_ohm << " Ом\n";
    printf("  Опір втрат котушки R_котушки: %.2f Ом\n", res.r_coil_ohm);
    std::cout << "  Опір заземлення/кузова R_землі: " << in.ground_loss_ohm << " Ом\n";
    std::cout << "  Повний опір R_повн: " << res.r_total_ohm << " Ом\n";
    std::cout << "  ККД випромінювання η: " << res.efficiency_pct << " %\n";
    std::cout << "--------------------------------------------------------\n";
    std::cout << "Характеристики смуги та режими напруги:\n";
    std::cout << "  Добротність антени Q: " << std::setprecision(1) << res.q_ant << "\n";
    std::cout << "  Смуга пропускання BW (-3dB): " << res.bandwidth_khz << " кГц\n";
    std::cout << "  Теплові втрати на котушці: " << res.p_heat_watts << " Вт\n";
    std::cout << "  Пікова ВЧ-напруга V_peak: " << std::setprecision(0) << res.v_peak_volts 
              << " В (" << std::setprecision(2) << res.v_peak_volts / 1000.0 << " кВ)\n";
    std::cout << "========================================================\n";
}

int main() {
    AntennaInputs inputs{
        .freq_mhz = 7.10,
        .height_m = 1.80,
        .wire_radius_mm = 2.0,
        .ground_loss_ohm = 4.0,
        .coil_q = 200.0,
        .power_watts = 100.0,
        .coil_diam_cm = 5.0,
        .coil_len_cm = 8.0
    };

    auto result = LoadingCoilCalculator::calculate(inputs);

    if (result) {
        print_cpp_report(inputs, *result);
    } else {
        std::cerr << "Помилка: некоректні вхідні параметри для розрахунку!\n";
        return 1;
    }

    return 0;
}
