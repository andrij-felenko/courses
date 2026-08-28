#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Структура геометричних та фізичних параметрів датчика */
typedef struct {
    double membrane_side_um;   /* Півширина мембрани a, мкм */
    double membrane_thick_um;  /* Товщина мембрани h, мкм */
    double r0_300k_ohm;        /* Опір при 300K, Ом */
    double doping_cm3;         /* Концентрація домішок N, см⁻³ */
    double v_in_volts;         /* Напруга живлення моста, В */
    double pi_l_110;           /* Поздовжній коефіцієнт, 1/Па */
    double pi_t_110;           /* Поперечний коефіцієнт, 1/Па */
    double tcr1;               /* Первинний TCR, 1/K */
    double tcr2;               /* Вторинний TCR, 1/K² */
} mems_config_t;

/* Структура результатів розрахунку для заданої точки (P, T) */
typedef struct {
    double pressure_kPa;
    double temp_K;
    double sigma_L_MPa;
    double sigma_T_MPa;
    double p_factor;
    double r1_ohm;
    double r2_ohm;
    double r3_ohm;
    double r4_ohm;
    double v_out_mV;
    double sensitivity_mV_V_kPa;
    double resonant_freq_kHz;
} mems_result_t;

/* Розрахунок фактора Кандера P(N, T) */
static double calculate_kanda_factor(double doping_cm3, double temp_k) {
    double n_ref = 1.4e19;
    double term_n = pow(doping_cm3 / n_ref, 0.72);
    double term_t = pow(300.0 / temp_k, 0.85);
    return 1.0 / (1.0 + term_n * term_t);
}

/* Моделювання виходу датчика у точці (pressure_kPa, temp_k) */
bool simulate_mems_sensor(const mems_config_t *cfg, double pressure_kPa, double temp_k, mems_result_t *res) {
    if (!cfg || !res || pressure_kPa < 0.0 || temp_k < 50.0) {
        return false;
    }

    /* Переведення геометричних розмірів у метри */
    double a_m = cfg->membrane_side_um * 1e-6;
    double h_m = cfg->membrane_thick_um * 1e-6;
    double p_pa = pressure_kPa * 1000.0;

    /* Обчислення механічних напружень на кромці (Паскалі та МПа) */
    double geom_ratio = a_m / h_m;
    double sigma_L_pa = 0.308 * p_pa * geom_ratio * geom_ratio;
    double sigma_T_pa = 0.092 * p_pa * geom_ratio * geom_ratio;

    res->pressure_kPa = pressure_kPa;
    res->temp_K = temp_k;
    res->sigma_L_MPa = sigma_L_pa / 1e6;
    res->sigma_T_MPa = sigma_T_pa / 1e6;

    /* Резонансна частота (кГц) */
    double e_mod = 169e9;    /* Модуль Юнга 169 ГПа */
    double rho_m = 2330.0;   /* Густина 2330 кг/м³ */
    double nu = 0.06;
    double fn_hz = (1.654 * h_m / (a_m * a_m)) * sqrt(e_mod / (rho_m * (1.0 - nu * nu)));
    res->resonant_freq_kHz = fn_hz / 1000.0;

    /* Фактор Кандера та базовий опір R0(T) */
    res->p_factor = calculate_kanda_factor(cfg->doping_cm3, temp_k);
    double dt = temp_k - 300.0;
    double r0_t = cfg->r0_300k_ohm * (1.0 + cfg->tcr1 * dt + cfg->tcr2 * dt * dt);

    /* Відносна зміна опору п'єзорезисторів */
    double dr1_r0 = (cfg->pi_l_110 * sigma_L_pa + cfg->pi_t_110 * sigma_T_pa) * res->p_factor;
    double dr2_r0 = (cfg->pi_l_110 * sigma_T_pa + cfg->pi_t_110 * sigma_L_pa) * res->p_factor;

    res->r1_ohm = r0_t * (1.0 + dr1_r0);
    res->r3_ohm = res->r1_ohm; /* Поздовжня пара */

    res->r2_ohm = r0_t * (1.0 + dr2_r0);
    res->r4_ohm = res->r2_ohm; /* Поперечна пара */

    /* Вихідна напруга моста Вітстона */
    double num = res->r1_ohm * res->r3_ohm - res->r2_ohm * res->r4_ohm;
    double den = (res->r1_ohm + res->r2_ohm) * (res->r3_ohm + res->r4_ohm);
    double v_out_v = cfg->v_in_volts * (num / den);

    res->v_out_mV = v_out_v * 1000.0;

    if (pressure_kPa > 1e-6) {
        res->sensitivity_mV_V_kPa = res->v_out_mV / (cfg->v_in_volts * pressure_kPa);
    } else {
        res->sensitivity_mV_V_kPa = 0.0;
    }

    return true;
}

int main(void) {
    mems_config_t cfg = {
        .membrane_side_um = 500.0,   /* a = 500 мкм (мембрана 1×1 мм) */
        .membrane_thick_um = 20.0,   /* h = 20 мкм */
        .r0_300k_ohm = 2000.0,       /* R0 = 2 кОм */
        .doping_cm3 = 3.0e18,        /* N = 3×10¹⁸ см⁻³ (p-Si) */
        .v_in_volts = 5.0,           /* Vin = 5 В */
        .pi_l_110 = 71.8e-11,        /* pi_L = +71.8×10⁻¹¹ Pa⁻¹ */
        .pi_t_110 = -68.7e-11,       /* pi_T = -68.7×10⁻¹¹ Pa⁻¹ */
        .tcr1 = 1.2e-3,              /* TCR1 = +0.12%/K */
        .tcr2 = 2.5e-6               /* TCR2 = +0.00025%/K² */
    };

    printf("=== МОДЕЛЮВАННЯ MEMS-ДАТЧИКА ТИСКУ (C Implementation) ===\n");
    printf("Розмір мембрани: 1000x1000 мкм, Товщина: 20 мкм, Живлення: %.1f В\n\n", cfg.v_in_volts);

    printf("%-10s %-8s %-12s %-12s %-10s %-12s %-12s\n",
           "Тиск(кПа)", "Т(К)", "sigma_L(МПа)", "sigma_T(МПа)", "P_factor", "V_out(мВ)", "Чув(мВ/В/кПа)");
    printf("-----------------------------------------------------------------------------------\n");

    double test_pressures[] = {0.0, 20.0, 50.0, 100.0};
    double test_temps[] = {250.0, 300.0, 350.0};

    for (size_t t = 0; t < 3; ++t) {
        for (size_t p = 0; p < 4; ++p) {
            mems_result_t res;
            if (simulate_mems_sensor(&cfg, test_pressures[p], test_temps[t], &res)) {
                printf("%-10.1f %-8.1f %-12.2f %-12.2f %-10.4f %-12.2f %-12.4f\n",
                       res.pressure_kPa, res.temp_K, res.sigma_L_MPa, res.sigma_T_MPa,
                       res.p_factor, res.v_out_mV, res.sensitivity_mV_V_kPa);
            }
        }
        printf("-----------------------------------------------------------------------------------\n");
    }

    return 0;
}
