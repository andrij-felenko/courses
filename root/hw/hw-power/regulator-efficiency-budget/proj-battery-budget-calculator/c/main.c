#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    REG_LDO,
    REG_BUCK_PFM,
    REG_BUCK_PWM,
    REG_BUCK_BOOST
} RegulatorType;

typedef struct {
    RegulatorType type;
    double iq_ua;        /* струм спокою кіл керування, мкА */
    double k_sw;         /* лінійний комутаційний коефіцієнт, Вт/А */
    double r_eq;         /* еквівалентний опір силового тракту, Ом */
    double p_fixed_pwm;  /* фіксовані комутаційні втрати для жорсткого PWM, Вт */
} RegulatorParams;

typedef struct {
    const char *name;
    double duration_ms;  /* тривалість фази, мс */
    double current_ma;   /* струм навантаження, мА */
} LoadPhase;

typedef struct {
    double nominal_mah;      /* номінальна ємність, мА·год */
    double nominal_voltage;  /* середня робоча напруга, В */
    double usable_dod;       /* доступна глибина розряду (0.0 .. 1.0) */
    double self_discharge_pct_year; /* річний саморозряд, % */
} BatterySpec;

typedef struct {
    double total_time_s;
    double e_out_joules;
    double e_in_joules;
    double avg_efficiency;
    double avg_in_current_ma;
    double peak_loss_watts;
    double battery_life_days;
    double battery_life_years;
} SimulationResult;

/* Розрахунок миттєвих втрат потужності регулятора у ватах */
static double calculate_regulator_loss(const RegulatorParams *reg,
                                       double v_in, double v_out, double i_out_a) {
    double iq_a = reg->iq_ua * 1e-6;
    
    switch (reg->type) {
        case REG_LDO:
            /* P_loss = (V_in - V_out) * I_out + V_in * Iq */
            return (v_in - v_out) * i_out_a + v_in * iq_a;
            
        case REG_BUCK_PFM:
            /* P_loss = V_in * Iq + k_sw * I_out + R_eq * I_out^2 */
            return v_in * iq_a + reg->k_sw * i_out_a + reg->r_eq * i_out_a * i_out_a;
            
        case REG_BUCK_PWM:
            /* P_loss = P_fixed + k_sw * I_out + R_eq * I_out^2 */
            return reg->p_fixed_pwm + reg->k_sw * i_out_a + reg->r_eq * i_out_a * i_out_a;
            
        case REG_BUCK_BOOST:
            /* 4-Switch: подвійний опір та підвищені комутаційні втрати */
            return v_in * iq_a + 1.8 * reg->k_sw * i_out_a + 1.8 * reg->r_eq * i_out_a * i_out_a;
            
        default:
            return 0.0;
    }
}

/* Моделювання повного періоду циклу та розрахунок часу життя */
bool simulate_energy_budget(const LoadPhase *phases, size_t phase_count,
                            const RegulatorParams *reg, double v_in, double v_out,
                            const BatterySpec *bat, SimulationResult *res) {
    if (!phases || phase_count == 0 || !reg || !bat || !res) return false;

    double total_time_ms = 0.0;
    double e_out_j = 0.0;
    double e_in_j = 0.0;
    double peak_loss_w = 0.0;

    for (size_t i = 0; i < phase_count; ++i) {
        double dt_s = phases[i].duration_ms * 1e-3;
        double i_out_a = phases[i].current_ma * 1e-3;
        double p_out = v_out * i_out_a;
        double p_loss = calculate_regulator_loss(reg, v_in, v_out, i_out_a);
        double p_in = p_out + p_loss;

        if (p_loss > peak_loss_w) {
            peak_loss_w = p_loss;
        }

        e_out_j += p_out * dt_s;
        e_in_j += p_in * dt_s;
        total_time_ms += phases[i].duration_ms;
    }

    if (total_time_ms <= 0.0 || e_in_j <= 0.0) return false;

    double total_time_s = total_time_ms * 1e-3;
    res->total_time_s = total_time_s;
    res->e_out_joules = e_out_j;
    res->e_in_joules = e_in_j;
    res->avg_efficiency = e_out_j / e_in_j;
    res->peak_loss_watts = peak_loss_w;

    /* Середня вхідна потужність та середній струм з батареї */
    double avg_p_in = e_in_j / total_time_s;
    res->avg_in_current_ma = (avg_p_in / v_in) * 1e3;

    /* Корисна енергія батареї в Джоулях */
    double bat_capacity_ah = bat->nominal_mah * 1e-3;
    double total_bat_joules = bat_capacity_ah * bat->nominal_voltage * 3600.0;
    double usable_joules = total_bat_joules * bat->usable_dod;

    /* Врахування річного саморозряду */
    double effective_power_in = avg_p_in + (usable_joules * (bat->self_discharge_pct_year * 0.01 / (365.25 * 86400.0)));

    double total_seconds = usable_joules / effective_power_in;
    res->battery_life_days = total_seconds / 86400.0;
    res->battery_life_years = res->battery_life_days / 365.25;

    return true;
}

int main(void) {
    const LoadPhase iot_profile[] = {
        { "Deep Sleep",   9900.0,  0.015 },  /* 9.9 с, 15 мкА */
        { "Sensor Read",    30.0,  4.500 },  /* 30 мс, 4.5 мА */
        { "Compute Crypto", 20.0, 12.000 },  /* 20 мс, 12 мА */
        { "Radio TX Burst", 50.0, 95.000 }   /* 50 мс, 95 мА */
    };
    size_t phase_count = sizeof(iot_profile) / sizeof(iot_profile[0]);

    BatterySpec li_ion = {
        .nominal_mah = 1200.0,
        .nominal_voltage = 3.7,
        .usable_dod = 0.90,
        .self_discharge_pct_year = 3.0
    };

    RegulatorParams ldo_nano = {
        .type = REG_LDO,
        .iq_ua = 0.8,
        .k_sw = 0.0,
        .r_eq = 0.0,
        .p_fixed_pwm = 0.0
    };

    RegulatorParams buck_pfm = {
        .type = REG_BUCK_PFM,
        .iq_ua = 2.0,
        .k_sw = 0.035,
        .r_eq = 0.18,
        .p_fixed_pwm = 0.0
    };

    RegulatorParams buck_pwm = {
        .type = REG_BUCK_PWM,
        .iq_ua = 15.0,
        .k_sw = 0.040,
        .r_eq = 0.18,
        .p_fixed_pwm = 0.015  /* 15 мВт фіксованих втрат */
    };

    double v_in = 3.7;
    double v_out = 3.3;
    SimulationResult res;

    printf("=== ПОРІВНЯЛЬНИЙ АНАЛІЗ ЕНЕРГЕТИЧНОГО БЮДЖЕТУ ===\n\n");

    if (simulate_energy_budget(iot_profile, phase_count, &ldo_nano, v_in, v_out, &li_ion, &res)) {
        printf("[1] Нанопотужний LDO (Iq = 0.8 мкА):\n");
        printf("    Середньозважений ККД : %.2f %%\n", res.avg_efficiency * 100.0);
        printf("    Середній струм входу : %.3f мА\n", res.avg_in_current_ma);
        printf("    Пікові втрати тепла  : %.2f мВт\n", res.peak_loss_watts * 1e3);
        printf("    Автономність         : %.1f днів (%.2f років)\n\n", res.battery_life_days, res.battery_life_years);
    }

    if (simulate_energy_budget(iot_profile, phase_count, &buck_pfm, v_in, v_out, &li_ion, &res)) {
        printf("[2] Buck з підтримкою PFM (Iq = 2.0 мкА):\n");
        printf("    Середньозважений ККД : %.2f %%\n", res.avg_efficiency * 100.0);
        printf("    Середній струм входу : %.3f мА\n", res.avg_in_current_ma);
        printf("    Пікові втрати тепла  : %.2f мВт\n", res.peak_loss_watts * 1e3);
        printf("    Автономність         : %.1f днів (%.2f років)\n\n", res.battery_life_days, res.battery_life_years);
    }

    if (simulate_energy_budget(iot_profile, phase_count, &buck_pwm, v_in, v_out, &li_ion, &res)) {
        printf("[3] Класичний PWM Buck (без PFM, P_fix = 15 мВт):\n");
        printf("    Середньозважений ККД : %.2f %%\n", res.avg_efficiency * 100.0);
        printf("    Середній струм входу : %.3f мА\n", res.avg_in_current_ma);
        printf("    Пікові втрати тепла  : %.2f мВт\n", res.peak_loss_watts * 1e3);
        printf("    Автономність         : %.1f днів (%.2f років)\n", res.battery_life_days, res.battery_life_years);
    }

    return 0;
}
