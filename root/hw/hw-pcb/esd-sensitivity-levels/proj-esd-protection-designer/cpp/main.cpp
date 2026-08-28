#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <expected>

namespace esd {

enum class StandardType {
    Iec61000_4_2,
    HbmJs001,
    CdmJs002
};

struct TvsParameters {
    std::string name{"Generic_TVS"};
    double v_rwm{3.3};          // Робоча напруга, В
    double v_br{5.0};           // Напруга пробою, В
    double v_hold{3.8};         // Напруга утримання (Snapback), В
    double v_trigger{7.5};      // Тригерна напруга, В
    double r_dyn{0.22};         // Динамічний опір, Ом
    double c_j_pf{0.28};        // Бар'єрна ємність, пФ
    double l_pkg_nh{0.35};      // Паразитна індуктивність корпусу, нГн
    bool is_snapback{true};     // Структура Snapback
};

struct IcTargetParameters {
    double v_breakdown_oxide{11.5}; // Поріг руйнування діелектрика затвора, В
    double v_on_internal{0.85};     // Поріг відкривання внутрішніх діодів, В
    double r_dyn_internal{2.40};    // Динамічний опір внутрішнього захисту, Ом
    double i_fail_internal{1.50};   // Граничний безпечний струм кристала, А
};

struct PcbLayoutParameters {
    double l_trace_nh{1.20};      // Індуктивність підвідної траси, нГн
    double r_series_ohm{15.0};    // Послідовний резистор SEED, Ом
    double z0_line_ohm{50.0};     // Хвильовий опір лінії, Ом
    double signal_freq_ghz{5.0};  // Робоча частота сигналу, ГГц
};

struct SimulationMetrics {
    double i_peak_esd{0.0};
    double v_tvs_clamp_peak{0.0};
    double v_inductive_peak{0.0};
    double v_node_total_peak{0.0};
    double v_ic_pin_peak{0.0};
    double i_ic_max{0.0};
    double energy_tvs_mj{0.0};
    double cutoff_freq_ghz{0.0};
    double s21_loss_db{0.0};
    double r_series_min_safe{0.0};
    bool is_oxide_safe{false};
    bool is_current_safe{false};
    bool is_latchup_safe{false};
};

class WaveformGenerator {
public:
    [[nodiscard]] static double get_iec_current(double t_ns, double v_kv) noexcept {
        if (t_ns <= 0.0) return 0.0;
        const double scale = v_kv / 8.0;
        constexpr double i1_base = 16.6;
        constexpr double k1 = 0.925;
        constexpr double tau1 = 0.6;
        constexpr double tau2 = 1.6;
        constexpr double n = 1.8;

        constexpr double i2_base = 9.3;
        constexpr double k2 = 0.940;
        constexpr double tau3 = 12.0;
        constexpr double tau4 = 47.0;

        const double t_tau1_n = std::pow(t_ns / tau1, n);
        const double term1 = (i1_base * scale / k1) * (t_tau1_n / (1.0 + t_tau1_n)) * std::exp(-t_ns / tau2);

        const double t_tau3_n = std::pow(t_ns / tau3, n);
        const double term2 = (i2_base * scale / k2) * (t_tau3_n / (1.0 + t_tau3_n)) * std::exp(-t_ns / tau4);

        return term1 + term2;
    }

    [[nodiscard]] static double get_hbm_current(double t_ns, double v_kv) noexcept {
        if (t_ns <= 0.0) return 0.0;
        const double i_peak = (v_kv * 1000.0) / 1500.0;
        constexpr double tau_rise = 2.27;
        constexpr double tau_decay = 150.0;
        return i_peak * (1.0 - std::exp(-t_ns / tau_rise)) * std::exp(-t_ns / tau_decay);
    }

    [[nodiscard]] static double get_cdm_current(double t_ns, double v_kv) noexcept {
        if (t_ns <= 0.0) return 0.0;
        const double i_peak = 12.0 * (v_kv / 0.500);
        constexpr double t_peak = 0.25;
        return i_peak * (t_ns / t_peak) * std::exp(1.0 - (t_ns / t_peak));
    }
};

class ProtectionSimulator {
public:
    static constexpr double SIM_TIME_MAX_NS = 120.0;
    static constexpr double SIM_TIME_STEP_NS = 0.010;
    static constexpr std::size_t SIM_POINTS = static_cast<std::size_t>(SIM_TIME_MAX_NS / SIM_TIME_STEP_NS) + 1;

    [[nodiscard]] static std::expected<SimulationMetrics, std::string_view> evaluate(
        const TvsParameters& tvs,
        const IcTargetParameters& ic,
        const PcbLayoutParameters& pcb,
        StandardType std_type,
        double v_stress_kv,
        double v_supply_line_v) noexcept
    {
        if (v_stress_kv <= 0.0) {
            return std::unexpected("Напруга стресу повинна бути більшою за нуль.");
        }

        SimulationMetrics m{};
        const double l_total_h = (tvs.l_pkg_nh + pcb.l_trace_nh) * 1e-9;
        constexpr double dt_s = SIM_TIME_STEP_NS * 1e-9;

        double prev_i = 0.0;
        double energy_joules = 0.0;

        for (std::size_t step = 0; step < SIM_POINTS; ++step) {
            const double t_ns = step * SIM_TIME_STEP_NS;
            double i_total = 0.0;

            switch (std_type) {
                case StandardType::Iec61000_4_2:
                    i_total = WaveformGenerator::get_iec_current(t_ns, v_stress_kv);
                    break;
                case StandardType::HbmJs001:
                    i_total = WaveformGenerator::get_hbm_current(t_ns, v_stress_kv);
                    break;
                case StandardType::CdmJs002:
                    i_total = WaveformGenerator::get_cdm_current(t_ns, v_stress_kv);
                    break;
            }

            m.i_peak_esd = std::max(m.i_peak_esd, i_total);

            const double di_dt = (i_total - prev_i) / dt_s;
            prev_i = i_total;

            const double v_ind = std::max(0.0, l_total_h * di_dt);
            m.v_inductive_peak = std::max(m.v_inductive_peak, v_ind);

            const double v_base_tvs = tvs.is_snapback ? tvs.v_hold : tvs.v_br;
            const double num = v_base_tvs + (i_total * tvs.r_dyn) - ic.v_on_internal;
            const double den = pcb.r_series_ohm + ic.r_dyn_internal + tvs.r_dyn;

            double i_ic = (num > 0.0) ? (num / den) : 0.0;
            i_ic = std::clamp(i_ic, 0.0, i_total);
            const double i_tvs = std::max(0.0, i_total - i_ic);

            const double v_tvs_semi = (i_tvs > 0.0) ? (v_base_tvs + i_tvs * tvs.r_dyn) : 0.0;
            m.v_tvs_clamp_peak = std::max(m.v_tvs_clamp_peak, v_tvs_semi);

            const double v_node_total = v_tvs_semi + v_ind;
            m.v_node_total_peak = std::max(m.v_node_total_peak, v_node_total);

            const double v_pin_ic = v_node_total - (i_ic * pcb.r_series_ohm);
            m.v_ic_pin_peak = std::max(m.v_ic_pin_peak, v_pin_ic);
            m.i_ic_max = std::max(m.i_ic_max, i_ic);

            energy_joules += (v_tvs_semi * i_tvs) * dt_s;
        }

        m.energy_tvs_mj = energy_joules * 1000.0;

        const double c_farads = tvs.c_j_pf * 1e-12;
        m.cutoff_freq_ghz = (1.0 / (std::numbers::pi * pcb.z0_line_ohm * c_farads)) * 1e-9;

        const double f_hz = pcb.signal_freq_ghz * 1e9;
        const double omega = 2.0 * std::numbers::pi * f_hz;
        const double s21_sq = 1.0 / (1.0 + std::pow(0.5 * omega * c_farads * pcb.z0_line_ohm, 2.0));
        m.s21_loss_db = 10.0 * std::log10(s21_sq);

        const double v_base_tvs = tvs.is_snapback ? tvs.v_hold : tvs.v_br;
        const double r_req = ((v_base_tvs + m.i_peak_esd * tvs.r_dyn - ic.v_on_internal) 
                             / ic.i_fail_internal) - ic.r_dyn_internal - tvs.r_dyn;
        m.r_series_min_safe = std::max(0.0, r_req);

        m.is_oxide_safe = (m.v_ic_pin_peak < ic.v_breakdown_oxide);
        m.is_current_safe = (m.i_ic_max < ic.i_fail_internal);
        m.is_latchup_safe = !tvs.is_snapback || (tvs.v_hold > (1.10 * v_supply_line_v));

        return m;
    }
};

void print_report(
    const TvsParameters& tvs,
    const IcTargetParameters& ic,
    const PcbLayoutParameters& pcb,
    StandardType std_type,
    double v_stress_kv,
    double v_supply_v,
    const SimulationMetrics& m)
{
    constexpr std::string_view std_names[] = {
        "IEC 61000-4-2 (Системний рівень)",
        "ANSI/ESDA/JEDEC JS-001 (HBM)",
        "ANSI/ESDA/JEDEC JS-002 (CDM)"
    };

    std::cout << "\n======================================================================\n";
    std::cout << "   C++20 ЗВІТ СИМУЛЯЦІЇ ESD-ЗАХИСТУ ТА ОЦІНКИ SEED КООРДИНАЦІЇ        \n";
    std::cout << "======================================================================\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << " 1. ПАРАМЕТРИ ВИПРОБУВАННЯ:\n";
    std::cout << "    • Стандарт:               " << std_names[static_cast<int>(std_type)] << '\n';
    std::cout << "    • Напруга стресу:         " << v_stress_kv << " кВ\n";
    std::cout << "    • Піковий струм імпульсу: " << m.i_peak_esd << " А\n";
    std::cout << "    • Напруга шини V_supply:  " << v_supply_v << " В\n";
    std::cout << "----------------------------------------------------------------------\n";
    std::cout << " 2. ХАРАКТЕРИСТИКИ TVS (" << tvs.name << "):\n";
    std::cout << "    • Робоча напруга V_RWM:   " << tvs.v_rwm << " В\n";
    std::cout << "    • Пробій V_BR / Тригер:   " << tvs.v_br << " В / " << tvs.v_trigger << " В\n";
    std::cout << "    • Тип напівпровідника:    " << (tvs.is_snapback ? "Snapback SCR" : "Zener Avalanche") << '\n';
    if (tvs.is_snapback) {
        std::cout << "    • Напруга утримання V_h:  " << tvs.v_hold << " В\n";
    }
    std::cout << std::setprecision(3);
    std::cout << "    • Динамічний опір R_dyn:  " << tvs.r_dyn << " Ом\n";
    std::cout << "    • Бар'єрна ємність C_j:   " << tvs.c_j_pf << " пФ\n";
    std::cout << std::setprecision(2);
    std::cout << "----------------------------------------------------------------------\n";
    std::cout << " 3. ДИНАМІЧНИЙ ВІДГУК ТА ПЕРЕНАПРУГИ:\n";
    std::cout << "    • Індуктивний викид:      +" << m.v_inductive_peak << " В  [L_total * di/dt]\n";
    std::cout << "    • Напруга TVS-переходу:   " << m.v_tvs_clamp_peak << " В  [V_semi]\n";
    std::cout << "    • Залишок на вході плати: " << m.v_node_total_peak << " В  [V_node]\n";
    std::cout << "    • Залишок на виводі IC:   " << m.v_ic_pin_peak << " В  [V_pin_IC]\n";
    std::cout << std::setprecision(3);
    std::cout << "    • Струм крізь кристал IC: " << m.i_ic_max << " А (" 
              << (m.i_ic_max / m.i_peak_esd) * 100.0 << "% від повного струму)\n";
    std::cout << "    • Поглинута енергія TVS:  " << m.energy_tvs_mj << " мДж\n";
    std::cout << std::setprecision(2);
    std::cout << "    • Безпечний R_series_min: " << m.r_series_min_safe << " Ом\n";
    std::cout << "----------------------------------------------------------------------\n";
    std::cout << " 4. ВИСОКОЧАСТОТНА СИГНАЛЬНА ЦІЛІСНІСТЬ:\n";
    std::cout << "    • Частота зрізу (-3 дБ):  " << m.cutoff_freq_ghz << " ГГц\n";
    std::cout << "    • Втрати на " << pcb.signal_freq_ghz << " ГГц:     " << m.s21_loss_db << " дБ (S21)\n";
    std::cout << "----------------------------------------------------------------------\n";
    std::cout << " 5. КРИТЕРІЇ ВАЛІДАЦІЇ СИСТЕМИ:\n";
    std::cout << "    [" << (m.is_oxide_safe ? " УСПІХ " : "ДЕФЕКТ") << "] Діелектрик затвора (" 
              << m.v_ic_pin_peak << " В < " << ic.v_breakdown_oxide << " В)\n";
    std::cout << "    [" << (m.is_current_safe ? " УСПІХ " : "ДЕФЕКТ") << "] Струм кристала (" 
              << m.i_ic_max << " А < " << ic.i_fail_internal << " А)\n";
    std::cout << "    [" << (m.is_latchup_safe ? " УСПІХ " : "ДЕФЕКТ") << "] Захист від Latch-up ("
              << (tvs.is_snapback ? (m.is_latchup_safe ? "V_hold > 1.1*V_supply" : "V_hold <= V_supply!") : "Zener N/A") << ")\n";
    std::cout << "======================================================================\n\n";
}

} // namespace esd

int main() {
    using namespace esd;

    const TvsParameters tvs_snap{
        .name = "TPD4E05U06_Snapback",
        .v_rwm = 3.3,
        .v_br = 5.5,
        .v_hold = 3.6,
        .v_trigger = 7.0,
        .r_dyn = 0.18,
        .c_j_pf = 0.25,
        .l_pkg_nh = 0.30,
        .is_snapback = true
    };

    const IcTargetParameters ic_target{
        .v_breakdown_oxide = 11.0,
        .v_on_internal = 0.80,
        .r_dyn_internal = 2.20,
        .i_fail_internal = 1.20
    };

    const PcbLayoutParameters pcb_layout{
        .l_trace_nh = 0.90,       // 0.9 мм компактної траси
        .r_series_ohm = 18.0,     // 18 Ом демпфувальний резистор
        .z0_line_ohm = 50.0,
        .signal_freq_ghz = 5.0    // USB 3.2 Gen2
    };

    // Випробування 8 кВ IEC 61000-4-2
    auto res_iec = ProtectionSimulator::evaluate(tvs_snap, ic_target, pcb_layout,
                                                 StandardType::Iec61000_4_2, 8.0, 3.3);
    if (res_iec) {
        print_report(tvs_snap, ic_target, pcb_layout, StandardType::Iec61000_4_2, 8.0, 3.3, *res_iec);
    } else {
        std::cerr << "Помилка: " << res_iec.error() << '\n';
    }

    // Випробування CDM 500 В
    auto res_cdm = ProtectionSimulator::evaluate(tvs_snap, ic_target, pcb_layout,
                                                 StandardType::CdmJs002, 0.500, 3.3);
    if (res_cdm) {
        print_report(tvs_snap, ic_target, pcb_layout, StandardType::CdmJs002, 0.500, 3.3, *res_cdm);
    }

    return 0;
}
