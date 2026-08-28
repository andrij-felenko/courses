#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NUM_POINTS 1000
#define DT_SEC     1.0e-9 // 1 наносекунда крок

typedef struct {
    double time_ns;
    double v_iso_volts;
    double dv_dt_v_per_us;
    double i_disp_ma;
    int unshielded_trigger;
    int shielded_trigger;
} cmti_point_t;

void simulate_cmti(double c_iso_pf, double v_step_volts, double rise_time_ns, cmti_point_t *out_data) {
    double c_iso_farads = c_iso_pf * 1.0e-12;
    double i_photodiode_threshold_ma = 2.0; // Поріг спрацьовування детектора
    
    for (int i = 0; i < NUM_POINTS; i++) {
        double t = i * DT_SEC * 1.0e9; // у наносекундах
        double v_iso = 0.0;
        double dv_dt = 0.0;

        // Формування імпульсу напруги з лінійним фронтом
        if (t >= 10.0 && t <= (10.0 + rise_time_ns)) {
            double progress = (t - 10.0) / rise_time_ns;
            v_iso = v_step_volts * progress;
            dv_dt = (v_step_volts / (rise_time_ns * 1.0e-9)) / 1.0e6; // В/мкс
        } else if (t > (10.0 + rise_time_ns)) {
            v_iso = v_step_volts;
            dv_dt = 0.0;
        }

        // I_disp = C_iso * dV/dt (у міліамперах)
        double i_disp = (c_iso_farads * (dv_dt * 1.0e6)) * 1000.0;

        out_data[i].time_ns = t;
        out_data[i].v_iso_volts = v_iso;
        out_data[i].dv_dt_v_per_us = dv_dt;
        out_data[i].i_disp_ma = i_disp;

        // Для неекранованого оптрона струм зміщення потрапляє у детектор
        out_data[i].unshielded_trigger = (i_disp > i_photodiode_threshold_ma) ? 1 : 0;
        
        // Для екранованого оптрона струм шунтується екраном Фарадея на 99.5%
        double i_shielded_residual = i_disp * 0.005;
        out_data[i].shielded_trigger = (i_shielded_residual > i_photodiode_threshold_ma) ? 1 : 0;
    }
}

int main(void) {
    cmti_point_t *results = (cmti_point_t *)malloc(sizeof(cmti_point_t) * NUM_POINTS);
    if (!results) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    // Симуляція фронту 600 В за 15 нс (dV/dt = 40 кВ/мкс) при C_iso = 0.6 пФ
    simulate_cmti(0.6, 600.0, 15.0, results);

    printf("Час(нс) | V_iso(В) | dV/dt(кВ/мкс) | I_disp(мА) | Без екрана | З екраном\n");
    printf("-----------------------------------------------------------------------\n");
    for (int i = 8; i <= 28; i += 2) {
        printf("%7.1f | %8.1f | %13.1f | %10.2f | %10s | %9s\n",
               results[i].time_ns,
               results[i].v_iso_volts,
               results[i].dv_dt_v_per_us,
               results[i].i_disp_ma,
               results[i].unshielded_trigger ? "ПОМИЛКА!" : "ОК",
               results[i].shielded_trigger ? "ПОМИЛКА!" : "ОК");
    }

    free(results);
    return 0;
}
