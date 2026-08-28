#include <iostream>
#include <iomanip>
#include <cmath>
#include <span>
#include <vector>
#include <string_view>

namespace emc {

constexpr double Cispr32ClassB3mLimitDbuv = 40.0;

struct CapacitiveCouplingParams {
    double mutual_capacitance_pf{3.0};
    double aggressor_dv{3.3};
    double rise_time_ns{1.0};
    double victim_impedance_ohm{10000.0};
};

struct InductiveCouplingParams {
    double mutual_inductance_nh{4.5};
    double aggressor_di{2.0};
    double rise_time_ns{5.0};
};

struct GroundBounceParams {
    double common_resistance_mohm{5.0};
    double common_inductance_nh{2.5};
    double pulse_current_a{4.0};
    double rise_time_ns{2.0};
};

struct RadiationParams {
    double frequency_mhz{100.0};
    double loop_area_cm2{1.5};
    double diff_current_ma{25.0};
    double cable_length_m{1.2};
    double common_mode_current_ua{8.0};
    double distance_m{3.0};
};

struct RadiationResult {
    double dm_field_dbuv{0.0};
    double cm_field_dbuv{0.0};
    bool passes_dm{true};
    bool passes_cm{true};
};

[[nodiscard]] auto calculate_capacitive_noise(const CapacitiveCouplingParams& p) noexcept {
    const double c_farads = p.mutual_capacitance_pf * 1e-12;
    const double dt_sec = p.rise_time_ns * 1e-9;
    const double dv_dt = p.aggressor_dv / dt_sec;
    const double current_a = c_farads * dv_dt;
    const double voltage_drop = current_a * p.victim_impedance_ohm;
    return std::pair{current_a * 1e3, voltage_drop}; // {мА, В}
}

[[nodiscard]] constexpr double calculate_inductive_noise(const InductiveCouplingParams& p) noexcept {
    const double m_henry = p.mutual_inductance_nh * 1e-9;
    const double dt_sec = p.rise_time_ns * 1e-9;
    const double di_dt = p.aggressor_di / dt_sec;
    return m_henry * di_dt;
}

[[nodiscard]] constexpr double calculate_ground_bounce(const GroundBounceParams& p) noexcept {
    const double r_ohm = p.common_resistance_mohm * 1e-3;
    const double l_henry = p.common_inductance_nh * 1e-9;
    const double dt_sec = p.rise_time_ns * 1e-9;
    const double di_dt = p.pulse_current_a / dt_sec;
    return (p.pulse_current_a * r_ohm) + (l_henry * di_dt);
}

[[nodiscard]] auto calculate_radiated_field(const RadiationParams& p) noexcept {
    const double f_hz = p.frequency_mhz * 1e6;
    const double a_m2 = p.loop_area_cm2 * 1e-4;
    const double i_dm_a = p.diff_current_ma * 1e-3;
    const double i_cm_a = p.common_mode_current_ua * 1e-6;

    const double e_dm_vm = (2.632e-14 * f_hz * f_hz * i_dm_a * a_m2) / p.distance_m;
    const double e_dm_uvm = e_dm_vm * 1e6;
    const double e_dm_db = 20.0 * std::log10(e_dm_uvm > 1e-9 ? e_dm_uvm : 1e-9);

    const double e_cm_vm = (1.257e-6 * f_hz * i_cm_a * p.cable_length_m) / p.distance_m;
    const double e_cm_uvm = e_cm_vm * 1e6;
    const double e_cm_db = 20.0 * std::log10(e_cm_uvm > 1e-9 ? e_cm_uvm : 1e-9);

    return RadiationResult{
        .dm_field_dbuv = e_dm_db,
        .cm_field_dbuv = e_cm_db,
        .passes_dm = (e_dm_db <= Cispr32ClassB3mLimitDbuv),
        .passes_cm = (e_cm_db <= Cispr32ClassB3mLimitDbuv)
    };
}

} // namespace emc

int main() {
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== Інженерний розрахунок параметрів ЕМС (C++) ===\n\n";

    emc::CapacitiveCouplingParams cap{};
    auto [inj_ma, v_cap] = emc::calculate_capacitive_noise(cap);
    std::cout << "1. Ємнісний зв'язок:\n"
              << "   Паразитна ємність: " << cap.mutual_capacitance_pf << " пФ, фронт: " << cap.rise_time_ns << " нс\n"
              << "   Впорснутий струм: " << inj_ma << " мА -> Напруга: " << v_cap << " В\n\n";

    emc::InductiveCouplingParams ind{};
    double v_ind = emc::calculate_inductive_noise(ind);
    std::cout << "2. Індуктивний зв'язок:\n"
              << "   Взаємна індуктивність: " << ind.mutual_inductance_nh << " нГн, струм: " << ind.aggressor_di << " А\n"
              << "   Наведена напруга: " << v_ind << " В (" << v_ind * 1e3 << " мВ)\n\n";

    emc::GroundBounceParams gb{};
    double v_gb = emc::calculate_ground_bounce(gb);
    std::cout << "3. Зсув опорного нуля (Ground Bounce):\n"
              << "   Спільна земля: " << gb.common_resistance_mohm << " мОм, " << gb.common_inductance_nh << " нГн\n"
              << "   Стрибок потенціалу землі: " << v_gb << " В (" << v_gb * 1e3 << " мВ)\n\n";

    emc::RadiationParams rad{};
    auto res = emc::calculate_radiated_field(rad);
    std::cout << "4. Випромінюване поле на частоті " << rad.frequency_mhz << " МГц (дистанція " << rad.distance_m << " м):\n"
              << "   Контур (DM): " << res.dm_field_dbuv << " дБмкВ/м [" << (res.passes_dm ? "ПРОЙДЕНО" : "ПЕРЕВИЩЕННЯ") << "]\n"
              << "   Кабель (CM): " << res.cm_field_dbuv << " дБмкВ/м [" << (res.passes_cm ? "ПРОЙДЕНО" : "ПЕРЕВИЩЕННЯ") << "]\n";

    return 0;
}
