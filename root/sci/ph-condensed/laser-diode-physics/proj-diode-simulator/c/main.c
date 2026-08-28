#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define CONST_Q 1.602176634e-19
#define CONST_HC 1.98644586e-25

typedef struct {
    double lambda_0_nm;  /* Довжина хвилі при T_ref (нм) */
    double I_th0_mA;     /* Пороговий струм при T_ref (мА) */
    double T_0_K;        /* Характерна температура Фікса (К) */
    double eta_d;        /* Диференціальна квантова ефективність */
    double R_s_ohm;      /* Омічний опір (Ом) */
    double R_th_KW;      /* Тепловий опір (К/Вт) */
    double dlambda_dT;   /* Температурний коефіцієнт λ (нм/К) */
    double T_sub_C;      /* Температура радіатора (°C) */
} DiodeParams;

typedef struct {
    double current_mA;
    double voltage_V;
    double power_mW;
    double temp_C;
    double lambda_nm;
    double wpe_percent;  /* Wall-Plug Efficiency (%) */
} SimPoint;

void simulate_laser_diode(const DiodeParams* params, double I_max_mA, double I_step_mA, 
                          SimPoint* results, size_t* out_count) {
    size_t count = 0;
    const double T_ref = 20.0; /* °C */
    const double photon_energy_eV = (CONST_HC / (params->lambda_0_nm * 1e-9)) / CONST_Q;

    for (double I_mA = 0.0; I_mA <= I_max_mA; I_mA += I_step_mA) {
        double I_A = I_mA / 1000.0;
        
        /* Початкове наближення для температури активної зони */
        double T_j = params->T_sub_C;
        double V_val = 0.0;
        double P_opt_mW = 0.0;
        
        /* Ітераційне узгодження теплового балансу */
        for (int iter = 0; iter < 5; ++iter) {
            /* 1. Напруга на p-n переході */
            V_val = photon_energy_eV + I_A * params->R_s_ohm;
            
            /* 2. Пороговий струм при температурі T_j */
            double I_th_mA = params->I_th0_mA * exp((T_j - T_ref) / params->T_0_K);
            
            /* 3. Оптична потужність */
            if (I_mA > I_th_mA) {
                P_opt_mW = photon_energy_eV * params->eta_d * (I_mA - I_th_mA);
            } else {
                P_opt_mW = 0.001 * photon_energy_eV * I_mA; /* Спонтанний режим */
            }
            
            /* 4. Оновлення температури через теплові втрати */
            double P_elec_mW = I_mA * V_val;
            double Q_heat_W = (P_elec_mW - P_opt_mW) / 1000.0;
            if (Q_heat_W < 0.0) Q_heat_W = 0.0;
            
            T_j = params->T_sub_C + params->R_th_KW * Q_heat_W;
        }

        double lambda_nm = params->lambda_0_nm + params->dlambda_dT * (T_j - T_ref);
        double P_elec_mW = I_mA * V_val;
        double wpe = (P_elec_mW > 1e-6) ? (P_opt_mW / P_elec_mW) * 100.0 : 0.0;

        results[count].current_mA = I_mA;
        results[count].voltage_V = V_val;
        results[count].power_mW = P_opt_mW;
        results[count].temp_C = T_j;
        results[count].lambda_nm = lambda_nm;
        results[count].wpe_percent = wpe;
        count++;
    }
    *out_count = count;
}

int main(void) {
    DiodeParams params = {
        .lambda_0_nm = 808.0,
        .I_th0_mA = 40.0,
        .T_0_K = 140.0,
        .eta_d = 0.85,
        .R_s_ohm = 2.5,
        .R_th_KW = 35.0,
        .dlambda_dT = 0.28,
        .T_sub_C = 25.0
    };

    SimPoint results[100];
    size_t count = 0;
    simulate_laser_diode(&params, 150.0, 15.0, results, &count);

    printf("=== МОДЕЛЮВАННЯ ЛАЗЕРНОГО ДІОДА (C11) ===\n");
    printf("  I (мА) |  V (В)  | P (мВт) | T (°C) | λ (нм) | WPE (%%)\n");
    printf("---------+---------+---------+--------+--------+---------\n");
    for (size_t i = 0; i < count; ++i) {
        printf("  %6.1f | %7.3f | %7.2f | %6.1f | %6.1f | %6.2f\n",
               results[i].current_mA, results[i].voltage_V, results[i].power_mW,
               results[i].temp_C, results[i].lambda_nm, results[i].wpe_percent);
    }
    return 0;
}
