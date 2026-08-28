#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define R_SPEC 461.5       /* Питома газова стала водяної пари, Дж/(кг·К) */
#define T_CRIT 647.10      /* Критична температура води, К */
#define P_CRIT 22064000.0  /* Критичний тиск води, Па */
#define L_0 3150000.0      /* Базовий коефіцієнт теплоти випаровування, Дж/кг */
#define V_LIQ 0.001        /* Питомий об'єм рідкої води, м³/кг */

/* Структура термодинамічного стану */
typedef struct {
    double temp_k;     /* Температура, К */
    double press_pa;   /* Тиск, Па */
} State;

/* Розрахунок прихованої теплоти випаровування L(T) за формулою Вотсона */
static double latent_heat(double temp_k) {
    if (temp_k >= T_CRIT) return 0.0;
    double tau = 1.0 - (temp_k / T_CRIT);
    return L_0 * pow(tau, 0.38);
}

/* Обчислення нахилу dP/dT за рівнянням Клапейрона — Клаузіуса */
static double clapeyron_rhs(double temp_k, double press_pa) {
    if (temp_k >= T_CRIT || press_pa <= 0.0) return 0.0;
    
    double l_vap = latent_heat(temp_k);
    /* Коефіцієнт стисливості пари Z (реальний газ при високому тиску) */
    double z_factor = 1.0 - 0.05 * (press_pa / P_CRIT);
    if (z_factor < 0.5) z_factor = 0.5;

    double v_gas = (z_factor * R_SPEC * temp_k) / press_pa;
    double delta_v = v_gas - V_LIQ;
    if (delta_v <= 1e-9) return 0.0;

    return l_vap / (temp_k * delta_v);
}

/* Емпіричне рівняння Антуана для води (тиск у Па, Т у К) */
static double antoine_water_pa(double temp_k) {
    double temp_c = temp_k - 273.15;
    /* Параметри Антуана для води у діапазоні 0..100 °C */
    double a = 8.07131;
    double b = 1730.63;
    double c = 233.426;
    double p_mmHg = pow(10.0, a - (b / (c + temp_c)));
    return p_mmHg * 133.322; /* Конвертація мм рт. ст. -> Па */
}

/* Інтегрування одного кроку методом Рунге — Кутти 4-го порядку (RK4) */
static State rk4_step(State current, double dt_k) {
    State result = current;
    double t = current.temp_k;
    double p = current.press_pa;

    double k1 = clapeyron_rhs(t, p);
    double k2 = clapeyron_rhs(t + 0.5 * dt_k, p + 0.5 * dt_k * k1);
    double k3 = clapeyron_rhs(t + 0.5 * dt_k, p + 0.5 * dt_k * k2);
    double k4 = clapeyron_rhs(t + dt_k, p + dt_k * k3);

    result.temp_k += dt_k;
    result.press_pa += (dt_k / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
    return result;
}

int main(void) {
    /* Початкова точка: потрійна точка води (T = 273.16 K, P = 611.65 Pa) */
    State state = { 273.16, 611.65 };
    double t_end = 373.15; /* 100 °C */
    double dt = 1.0;       /* Крок по температурі 1 К */

    printf("T (C)  | P_Clapeyron (hPa) | P_Antoine (hPa) | Похилка (%%)\n");
    printf("-------+-------------------+-----------------+------------\n");

    while (state.temp_k <= t_end + 1e-5) {
        double temp_c = state.temp_k - 273.15;
        double p_hpa = state.press_pa / 100.0;
        double p_ant_hpa = antoine_water_pa(state.temp_k) / 100.0;
        double err_pct = fabs(p_hpa - p_ant_hpa) / p_ant_hpa * 100.0;

        if ((int)(temp_c + 0.5) % 10 == 0) {
            printf("%6.1f | %17.2f | %15.2f | %10.2f\n",
                   temp_c, p_hpa, p_ant_hpa, err_pct);
        }

        state = rk4_step(state, dt);
    }

    return 0;
}
