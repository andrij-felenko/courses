#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Результати розрахунку конденсаторного накопичувача */
typedef struct {
    double energy_joules;        /* Накопичена енергія E = 0.5 * C * V^2 */
    double peak_current_amperes; /* Піковий струм КЗ через ESR: I = V / ESR */
    double max_bleeder_ohms;     /* Максимальний опір розрядника для t_safe */
    double bleeder_power_watts;  /* Потужність втрат на розряднику P = V^2 / R */
    bool is_lethal_hazard;       /* Прапорець небезпеки фібриляції (> 10 Дж @ > 60 В) */
} CapSizingResult;

/* Результати розрахунку індуктивного викиду */
typedef struct {
    double energy_joules;        /* Магнітна енергія E = 0.5 * L * I^2 */
    double unsuppressed_v_spike; /* Розрахунковий викид напруги V = L * (I / dt) */
    double diode_decay_time_sec; /* Час спаду з діодом t ≈ 3.5 * L / R */
    double zener_decay_time_sec; /* Час спаду зі стабілітроном t ≈ L * I / Vz */
} IndSizingResult;

/* Результати розрахунку безпеки акумулятора */
typedef struct {
    double energy_joules;        /* Хімічна енергія E = V * Q (Дж) */
    double energy_watt_hours;    /* Енергія у Вт*год */
    double short_circuit_amps;   /* Струм короткого замикання I_sc = V / R_int */
    double peak_sc_power_watts;  /* Пікова теплова потужність P = I^2 * R_int */
    double adiabatic_heat_rate;  /* Темп адіабатичного нагріву (°C / c) */
    double time_to_85c_seconds;  /* Час до критичної точки SEI розпаду (85 °C) */
} BatterySizingResult;

/* Розрахунок параметрів безпеки конденсатора */
CapSizingResult calculate_capacitor_safety(double capacitance_farads,
                                           double voltage_volts,
                                           double esr_ohms,
                                           double target_safe_time_sec,
                                           double target_safe_voltage_volts)
{
    CapSizingResult res;
    res.energy_joules = 0.5 * capacitance_farads * voltage_volts * voltage_volts;
    res.peak_current_amperes = (esr_ohms > 0.0) ? (voltage_volts / esr_ohms) : 0.0;
    
    if (voltage_volts > target_safe_voltage_volts && target_safe_time_sec > 0.0) {
        double ln_ratio = log(voltage_volts / target_safe_voltage_volts);
        res.max_bleeder_ohms = target_safe_time_sec / (capacitance_farads * ln_ratio);
        res.bleeder_power_watts = (voltage_volts * voltage_volts) / res.max_bleeder_ohms;
    } else {
        res.max_bleeder_ohms = 0.0;
        res.bleeder_power_watts = 0.0;
    }
    
    res.is_lethal_hazard = (res.energy_joules >= 10.0 && voltage_volts >= 60.0);
    return res;
}

/* Розрахунок параметрів індуктивного навантаження */
IndSizingResult calculate_inductor_safety(double inductance_henry,
                                          double current_amperes,
                                          double coil_resistance_ohms,
                                          double switch_turn_off_time_sec,
                                          double zener_voltage_volts)
{
    IndSizingResult res;
    res.energy_joules = 0.5 * inductance_henry * current_amperes * current_amperes;
    
    if (switch_turn_off_time_sec > 0.0) {
        res.unsuppressed_v_spike = inductance_henry * (current_amperes / switch_turn_off_time_sec);
    } else {
        res.unsuppressed_v_spike = 0.0;
    }
    
    if (coil_resistance_ohms > 0.0) {
        res.diode_decay_time_sec = 3.5 * (inductance_henry / coil_resistance_ohms);
    } else {
        res.diode_decay_time_sec = 0.0;
    }
    
    if (zener_voltage_volts > 0.0) {
        res.zener_decay_time_sec = (inductance_henry * current_amperes) / zener_voltage_volts;
    } else {
        res.zener_decay_time_sec = 0.0;
    }
    
    return res;
}

/* Розрахунок теплового розгону акумулятора */
BatterySizingResult calculate_battery_safety(double voltage_volts,
                                             double capacity_amp_hours,
                                             double internal_resistance_ohms,
                                             double mass_kg,
                                             double initial_temp_celsius)
{
    BatterySizingResult res;
    const double specific_heat_capacity = 1000.0; /* Дж / (кг * °C) для Li-ion */
    const double critical_sei_temp = 85.0;        /* Початок руйнування SEI */
    
    res.energy_watt_hours = voltage_volts * capacity_amp_hours;
    res.energy_joules = res.energy_watt_hours * 3600.0;
    
    if (internal_resistance_ohms > 0.0) {
        res.short_circuit_amps = voltage_volts / internal_resistance_ohms;
        res.peak_sc_power_watts = res.short_circuit_amps * res.short_circuit_amps * internal_resistance_ohms;
    } else {
        res.short_circuit_amps = 0.0;
        res.peak_sc_power_watts = 0.0;
    }
    
    if (mass_kg > 0.0) {
        res.adiabatic_heat_rate = res.peak_sc_power_watts / (mass_kg * specific_heat_capacity);
        double delta_t = critical_sei_temp - initial_temp_celsius;
        if (delta_t > 0.0 && res.adiabatic_heat_rate > 0.0) {
            res.time_to_85c_seconds = delta_t / res.adiabatic_heat_rate;
        } else {
            res.time_to_85c_seconds = 0.0;
        }
    } else {
        res.adiabatic_heat_rate = 0.0;
        res.time_to_85c_seconds = 0.0;
    }
    
    return res;
}
