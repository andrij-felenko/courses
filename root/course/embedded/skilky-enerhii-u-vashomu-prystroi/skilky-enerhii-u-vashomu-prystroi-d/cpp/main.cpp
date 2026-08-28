#include <cmath>
#include <expected>
#include <string_view>
#include <numbers>

namespace energy_safety {

enum class SizingError {
    InvalidParameter,
    DivisionByZero,
    NegativeTime
};

struct CapacitorReport {
    double energy_joules{0.0};
    double peak_current_amps{0.0};
    double max_bleeder_ohms{0.0};
    double bleeder_power_loss_watts{0.0};
    bool is_hazardous{false};
};

struct InductorReport {
    double energy_joules{0.0};
    double unsuppressed_spike_volts{0.0};
    double diode_decay_time_sec{0.0};
    double zener_decay_time_sec{0.0};
};

struct BatteryReport {
    double energy_joules{0.0};
    double energy_watt_hours{0.0};
    double short_circuit_amps{0.0};
    double short_circuit_power_watts{0.0};
    double heating_rate_deg_per_sec{0.0};
    double time_to_thermal_runaway_sec{0.0};
};

/* Розрахунок енергії та розрядного кола конденсатора */
[[nodiscard]] constexpr auto evaluate_capacitor(
    double capacitance_f,
    double voltage_v,
    double esr_ohms,
    double target_time_sec,
    double safe_voltage_v = 50.0) noexcept -> std::expected<CapacitorReport, SizingError>
{
    if (capacitance_f <= 0.0 || voltage_v < 0.0 || esr_ohms <= 0.0 || target_time_sec <= 0.0) {
        return std::unexpected(SizingError::InvalidParameter);
    }

    CapacitorReport rep{};
    rep.energy_joules = 0.5 * capacitance_f * voltage_v * voltage_v;
    rep.peak_current_amps = voltage_v / esr_ohms;

    if (voltage_v > safe_voltage_v) {
        const double ratio = voltage_v / safe_voltage_v;
        const double ln_ratio = std::log(ratio);
        rep.max_bleeder_ohms = target_time_sec / (capacitance_f * ln_ratio);
        rep.bleeder_power_loss_watts = (voltage_v * voltage_v) / rep.max_bleeder_ohms;
    }

    rep.is_hazardous = (rep.energy_joules >= 10.0 && voltage_v >= 60.0);
    return rep;
}

/* Розрахунок параметрів індуктивного викиду */
[[nodiscard]] constexpr auto evaluate_inductor(
    double inductance_h,
    double current_a,
    double coil_res_ohms,
    double switch_time_sec,
    double zener_v = 36.0) noexcept -> std::expected<InductorReport, SizingError>
{
    if (inductance_h <= 0.0 || current_a <= 0.0 || coil_res_ohms <= 0.0 || switch_time_sec <= 0.0) {
        return std::unexpected(SizingError::InvalidParameter);
    }

    InductorReport rep{};
    rep.energy_joules = 0.5 * inductance_h * current_a * current_a;
    rep.unsuppressed_spike_volts = inductance_h * (current_a / switch_time_sec);
    rep.diode_decay_time_sec = 3.5 * (inductance_h / coil_res_ohms);
    rep.zener_decay_time_sec = (zener_v > 0.0) ? ((inductance_h * current_a) / zener_v) : 0.0;

    return rep;
}

/* Розрахунок теплового розгону акумулятора */
[[nodiscard]] constexpr auto evaluate_battery(
    double voltage_v,
    double capacity_ah,
    double internal_res_ohms,
    double mass_kg,
    double ambient_temp_c = 25.0) noexcept -> std::expected<BatteryReport, SizingError>
{
    if (voltage_v <= 0.0 || capacity_ah <= 0.0 || internal_res_ohms <= 0.0 || mass_kg <= 0.0) {
        return std::unexpected(SizingError::InvalidParameter);
    }

    constexpr double specific_heat = 1000.0; // Дж / (кг * °C)
    constexpr double sei_critical_temp = 85.0; // °C

    BatteryReport rep{};
    rep.energy_watt_hours = voltage_v * capacity_ah;
    rep.energy_joules = rep.energy_watt_hours * 3600.0;
    rep.short_circuit_amps = voltage_v / internal_res_ohms;
    rep.short_circuit_power_watts = rep.short_circuit_amps * rep.short_circuit_amps * internal_res_ohms;
    rep.heating_rate_deg_per_sec = rep.short_circuit_power_watts / (mass_kg * specific_heat);

    const double delta_t = sei_critical_temp - ambient_temp_c;
    if (delta_t > 0.0 && rep.heating_rate_deg_per_sec > 0.0) {
        rep.time_to_thermal_runaway_sec = delta_t / rep.heating_rate_deg_per_sec;
    }

    return rep;
}

} // namespace energy_safety
