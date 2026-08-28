#include <iostream>
#include <cmath>
#include <string_view>
#include <span>
#include <vector>
#include <optional>
#include <iomanip>

struct PowerStageParams {
    double v_rms_nominal;     // Номінальна напруга мережі, В
    double c_filter_uf;       // Ємність накопичувача, мкФ
    double r_inrush_ohms;     // Холодний опір NTC + проводів, Ом
    double p_load_watts;      // Вихідна потужність, Вт
    double efficiency;        // ККД перетворювача, 0..1
    double power_factor;      // Коефіцієнт потужності
    double t_ambient_c;       // Температура всередині приладу, °C
    int    target_cycles;     // Задана кількість циклів вмикання
};

struct FuseCandidate {
    std::string_view part_number;
    double current_rating_a;
    double i2t_melting_a2s;
};

struct SizingResult {
    double inrush_peak_a;
    double tau_ms;
    double inrush_i2t_a2s;
    double pulse_derating_factor;
    double required_i2t_a2s;
    double load_current_rms_a;
    double temp_derating_factor;
    double required_current_a;
    const FuseCandidate* selected_fuse;
};

constexpr double calculate_pulse_derating(int cycles) {
    if (cycles <= 1)      return 1.0;
    if (cycles <= 10)     return 0.70;
    if (cycles <= 100)    return 0.50;
    if (cycles <= 1000)   return 0.38;
    if (cycles <= 10000)  return 0.29;
    if (cycles <= 50000)  return 0.23;
    if (cycles <= 100000) return 0.20;
    return std::pow(static_cast<double>(cycles), -0.14);
}

constexpr double calculate_temp_derating(double temp_c) {
    if (temp_c <= 25.0) return 1.0;
    const double factor = 1.0 - 0.0035 * (temp_c - 25.0);
    return factor > 0.5 ? factor : 0.5;
}

std::optional<SizingResult> select_fuse(
    const PowerStageParams& params,
    std::span<const FuseCandidate> catalog,
    double min_grid_voltage_v = 180.0)
{
    const double v_peak = params.v_rms_nominal * std::sqrt(2.0);
    const double inrush_peak = v_peak / params.r_inrush_ohms;
    const double tau_sec = params.r_inrush_ohms * (params.c_filter_uf * 1e-6);
    const double inrush_i2t = 0.5 * (inrush_peak * inrush_peak) * tau_sec;

    const double k_pulse = calculate_pulse_derating(params.target_cycles);
    const double required_i2t = inrush_i2t / k_pulse;

    const double p_in = params.p_load_watts / params.efficiency;
    const double load_rms = p_in / (min_grid_voltage_v * params.power_factor);
    const double k_temp = calculate_temp_derating(params.t_ambient_c);
    const double required_i_nom = load_rms / (k_temp * 0.75);

    const FuseCandidate* best_match = nullptr;
    for (const auto& fuse : catalog) {
        if (fuse.current_rating_a >= required_i_nom &&
            fuse.i2t_melting_a2s >= required_i2t) {
            best_match = &fuse;
            break;
        }
    }

    if (!best_match) {
        return std::nullopt;
    }

    return SizingResult{
        .inrush_peak_a = inrush_peak,
        .tau_ms = tau_sec * 1000.0,
        .inrush_i2t_a2s = inrush_i2t,
        .pulse_derating_factor = k_pulse,
        .required_i2t_a2s = required_i2t,
        .load_current_rms_a = load_rms,
        .temp_derating_factor = k_temp,
        .required_current_a = required_i_nom,
        .selected_fuse = best_match
    };
}

int main() {
    constexpr PowerStageParams params{
        .v_rms_nominal = 230.0,
        .c_filter_uf = 470.0,
        .r_inrush_ohms = 10.5,
        .p_load_watts = 200.0,
        .efficiency = 0.88,
        .power_factor = 0.95,
        .t_ambient_c = 55.0,
        .target_cycles = 50000
    };

    static constexpr FuseCandidate catalog[] = {
        { "5x20mm T1.0A 250V",  1.0,   2.8  },
        { "5x20mm T1.6A 250V",  1.6,   6.5  },
        { "5x20mm T2.0A 250V",  2.0,  11.2  },
        { "5x20mm T2.5A 250V",  2.5,  18.5  },
        { "5x20mm T3.15A 250V", 3.15, 29.0  },
        { "5x20mm T4.0A 250V",  4.0,  46.0  },
        { "5x20mm T5.0A 250V",  5.0,  78.0  },
        { "5x20mm T6.3A 250V",  6.3, 130.0  }
    };

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== РОЗРАХУНОК ВХІДНОГО ЗАПОБІЖНИКА SMPS (C++20) ===\n";

    const auto result = select_fuse(params, catalog);
    if (!result) {
        std::cerr << "Помилка: не знайдено відповідного запобіжника у каталозі.\n";
        return 1;
    }

    std::cout << "Піковий пусковий струм: " << result->inrush_peak_a << " А (tau = "
              << result->tau_ms << " мс)\n";
    std::cout << "Пускова енергія I²t_inrush: " << result->inrush_i2t_a2s << " А²·с\n";
    std::cout << "Коефіцієнт дерайтингу (50 000 циклів): "
              << result->pulse_derating_factor << "\n";
    std::cout << "Мінімальний розрахунковий Melting I²t: >= "
              << result->required_i2t_a2s << " А²·с\n";
    std::cout << "Мінімальний розрахунковий номінальний струм: >= "
              << result->required_current_a << " А\n\n";

    std::cout << ">>> ОБРАНО: " << result->selected_fuse->part_number << " <<<\n";
    std::cout << "  Струм: " << result->selected_fuse->current_rating_a << " А\n";
    std::cout << "  Melting I²t: " << result->selected_fuse->i2t_melting_a2s << " А²·с\n";

    return 0;
}
