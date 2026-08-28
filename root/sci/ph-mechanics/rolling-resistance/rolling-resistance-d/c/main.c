#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define GRAVITY 9.81
#define AIR_DENSITY_STD 1.225

typedef struct {
    double mass_kg;             /* Повна маса транспортного засобу (кг) */
    double cd;                  /* Коефіцієнт лобового аеродинамічного опору */
    double frontal_area_m2;     /* Лобова площа проекції (м²) */
    double tire_radius_m;       /* Динамічний радіус колеса (м) */
    double tire_pressure_bar;   /* Внутрішній тиск у шинах (бар) */
    double crr_nominal;         /* Номінальний коефіцієнт кочення за тиску 2.5 бар */
    double gear_ratio;          /* Передавальне відношення редуктора */
    double gear_efficiency;     /* Механічний ККД трансмісії */
    double rot_inertia_coeff;   /* Коефіцієнт обертових мас (1 + delta) */
    double aux_power_w;         /* Потужність допоміжних систем (Вт) */
} VehicleParams;

typedef struct {
    double speed_mps;           /* Поточна швидкість руху (м/с) */
    double accel_mps2;          /* Лінійне прискорення (м/с²) */
    double grade_rad;           /* Кут нахилу дороги (радіани) */
    double headwind_mps;        /* Зустрічна швидкість вітру (м/с) */
    double air_density;         /* Густина повітря (кг/м³) */
} DynamicState;

typedef struct {
    double f_roll_n;            /* Сила опору коченню (Н) */
    double f_aero_n;            /* Сила аеродинамічного опору (Н) */
    double f_grade_n;           /* Сила опору підйому (Н) */
    double f_accel_n;           /* Сила інерційного прискорення (Н) */
    double f_total_wheel_n;     /* Сумарна тягова сила на колесах (Н) */
    double motor_torque_nm;     /* Необхідний момент на валу двигуна (Н·м) */
    double motor_speed_radps;   /* Кутова швидкість двигуна (рад/с) */
    double motor_power_mech_w;  /* Механічна потужність двигуна (Вт) */
    double motor_efficiency;    /* Розрахунковий ККД двигуна та інвертора */
    double battery_power_w;     /* Повна споживана електрична потужність від АКБ (Вт) */
} SimulationResult;

/* Розрахунок залежності C_rr від швидкості та тиску за модифікованою моделлю SAE */
double compute_rolling_coeff(const VehicleParams* veh, double speed_mps) {
    double p_ratio = 2.5 / veh->tire_pressure_bar;
    double pressure_factor = sqrt(p_ratio);
    double speed_factor = 1.0 + 0.0035 * (speed_mps * 3.6 / 100.0) + 
                          0.0020 * pow(speed_mps * 3.6 / 100.0, 2.0);
    return veh->crr_nominal * pressure_factor * speed_factor;
}

/* Модель розрахунку ККД PMSM електродвигуна з урахуванням мідних та магнітних втрат */
double compute_motor_efficiency(double torque_nm, double speed_radps) {
    double p_mech = fabs(torque_nm * speed_radps);
    if (p_mech < 50.0) return 0.65;
    
    double loss_copper = 0.0018 * (torque_nm * torque_nm);
    double loss_iron = 0.00035 * (speed_radps * speed_radps) + 0.08 * speed_radps;
    double loss_friction = 0.015 * speed_radps + 35.0;
    double total_loss = loss_copper + loss_iron + loss_friction;
    
    double eff = p_mech / (p_mech + total_loss);
    if (eff > 0.965) eff = 0.965;
    if (eff < 0.200) eff = 0.200;
    return eff;
}

/* Обчислення миттєвого тягового балансу та енергоспоживання */
SimulationResult simulate_step(const VehicleParams* veh, const DynamicState* state) {
    SimulationResult res;
    double normal_force = veh->mass_kg * GRAVITY * cos(state->grade_rad);
    double crr = compute_rolling_coeff(veh, state->speed_mps);
    
    res.f_roll_n = crr * normal_force;
    
    double air_speed = state->speed_mps + state->headwind_mps;
    res.f_aero_n = 0.5 * state->air_density * veh->cd * veh->frontal_area_m2 * (air_speed * air_speed);
    if (air_speed < 0.0) res.f_aero_n = -res.f_aero_n;
    
    res.f_grade_n = veh->mass_kg * GRAVITY * sin(state->grade_rad);
    res.f_accel_n = veh->mass_kg * state->accel_mps2 * veh->rot_inertia_coeff;
    
    res.f_total_wheel_n = res.f_roll_n + res.f_aero_n + res.f_grade_n + res.f_accel_n;
    
    double wheel_speed_radps = state->speed_mps / veh->tire_radius_m;
    res.motor_speed_radps = wheel_speed_radps * veh->gear_ratio;
    
    if (res.f_total_wheel_n >= 0.0) {
        res.motor_torque_nm = (res.f_total_wheel_n * veh->tire_radius_m) / 
                              (veh->gear_ratio * veh->gear_efficiency);
        res.motor_power_mech_w = res.motor_torque_nm * res.motor_speed_radps;
        res.motor_efficiency = compute_motor_efficiency(res.motor_torque_nm, res.motor_speed_radps);
        res.battery_power_w = (res.motor_power_mech_w / res.motor_efficiency) + veh->aux_power_w;
    } else {
        /* Режим рекуперативного електричного гальмування */
        res.motor_torque_nm = (res.f_total_wheel_n * veh->tire_radius_m * veh->gear_efficiency) / 
                              veh->gear_ratio;
        res.motor_power_mech_w = res.motor_torque_nm * res.motor_speed_radps;
        res.motor_efficiency = compute_motor_efficiency(res.motor_torque_nm, res.motor_speed_radps);
        res.battery_power_w = (res.motor_power_mech_w * res.motor_efficiency) + veh->aux_power_w;
    }
    
    return res;
}

int main(void) {
    VehicleParams ev = {
        .mass_kg = 1950.0,
        .cd = 0.23,
        .frontal_area_m2 = 2.25,
        .tire_radius_m = 0.33,
        .tire_pressure_bar = 2.5,
        .crr_nominal = 0.0080,
        .gear_ratio = 9.05,
        .gear_efficiency = 0.97,
        .rot_inertia_coeff = 1.05,
        .aux_power_w = 450.0
    };

    printf("=== МОДЕЛЮВАННЯ ТЯГОВОГО ЕЛЕКТРОПРИВОДУ (C) ===\n");
    printf("Маса: %.0f кг | Cd*A: %.3f м² | Номінальний Crr: %.4f\n\n", 
           ev.mass_kg, ev.cd * ev.frontal_area_m2, ev.crr_nominal);

    double test_speeds_kmh[] = {30.0, 60.0, 90.0, 120.0, 150.0};
    int n_tests = sizeof(test_speeds_kmh) / sizeof(test_speeds_kmh[0]);

    printf("%-8s | %-9s | %-9s | %-9s | %-10s | %-10s | %-12s\n",
           "V, км/год", "F_roll, Н", "F_aero, Н", "C_rr", "P_roll, кВт", "P_aero, кВт", "АКБ, кВт·год/100км");
    printf("------------------------------------------------------------------------------------\n");

    for (int i = 0; i < n_tests; ++i) {
        DynamicState st = {
            .speed_mps = test_speeds_kmh[i] / 3.6,
            .accel_mps2 = 0.0,
            .grade_rad = 0.0,
            .headwind_mps = 0.0,
            .air_density = AIR_DENSITY_STD
        };

        SimulationResult r = simulate_step(&ev, &st);
        double p_roll_kw = (r.f_roll_n * st.speed_mps) / 1000.0;
        double p_aero_kw = (r.f_aero_n * st.speed_mps) / 1000.0;
        double kwh_per_100km = (r.battery_power_w / 1000.0) / (test_speeds_kmh[i]) * 100.0;
        double current_crr = compute_rolling_coeff(&ev, st.speed_mps);

        printf("%8.1f | %9.1f | %9.1f | %9.5f | %10.2f | %10.2f | %12.2f\n",
               test_speeds_kmh[i], r.f_roll_n, r.f_aero_n, current_crr, 
               p_roll_kw, p_aero_kw, kwh_per_100km);
    }

    return 0;
}
