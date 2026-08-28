#include <stdio.h>
#include <math.h>
#include <stdbool.h>

typedef struct {
    double vdd;         // Напруга живлення, В
    double vth_n;       // Поріг NMOS, В
    double vth_p;       // Поріг PMOS (абсолютне значення), В
    double beta_n;      // Крутизна NMOS (mu * Cox * W/L), А/В^2
    double beta_p;      // Крутизна PMOS, А/В^2
    double c_load;      // Ємність навантаження, Ф
    double t_rise;      // Тривалість наростання входу, с
} CmosInverterParams;

typedef struct {
    double energy_cap_joules;   // Енергія заряду ємності
    double energy_sc_joules;    // Енергія наскрізного струму
    double energy_total_joules; // Повна динамічна енергія за фронт
    double peak_sc_current_a;   // Піковий наскрізний струм, А
} SimResults;

// Розрахунок струму стоку польового транзистора (модель Шихмана-Ходжеса)
static double calc_mos_current(double vgs, double vds, double vth, double beta) {
    if (vgs <= vth) {
        return 0.0; // Підпорогова зона (нехтуємо витоком для динаміки)
    }
    double vov = vgs - vth; // Надпорогова напруга (Overdrive)
    if (vds < vov) {
        // Лінійний режим
        return beta * (vov * vds - 0.5 * vds * vds);
    } else {
        // Режим насичення
        return 0.5 * beta * vov * vov;
    }
}

SimResults simulate_switching(const CmosInverterParams* p, double dt, double t_sim_end) {
    SimResults res = {0.0, 0.0, 0.0, 0.0};
    double v_out = p->vdd; // Початковий стан: вхід 0 -> вихід VDD
    double t = 0.0;

    while (t <= t_sim_end) {
        // Вхідна напруга (лінійний фронт 0 -> VDD)
        double v_in = (t < p->t_rise) ? (p->vdd * (t / p->t_rise)) : p->vdd;

        // Струми NMOS та PMOS
        double vgs_n = v_in;
        double vds_n = v_out;
        double i_nmos = calc_mos_current(vgs_n, vds_n, p->vth_n, p->beta_n);

        double vgs_p = p->vdd - v_in;
        double vds_p = p->vdd - v_out;
        double i_pmos = calc_mos_current(vgs_p, vds_p, p->vth_p, p->beta_p);

        // Наскрізний струм — це мінімальний струм, що тече крізь обидва транзистори
        double i_sc = (i_nmos < i_pmos) ? i_nmos : i_pmos;
        if (i_sc > res.peak_sc_current_a) {
            res.peak_sc_current_a = i_sc;
        }

        // Струм розряду навантажувальної ємності
        double i_cap = i_nmos - i_pmos;

        // Зміна напруги на виході: dv_out/dt = -i_cap / C_L
        double dv_out = -(i_cap / p->c_load) * dt;
        v_out += dv_out;
        if (v_out < 0.0) v_out = 0.0;
        if (v_out > p->vdd) v_out = p->vdd;

        // Інтегрування енергії: миттєва потужність джерела P_supply = VDD * i_pmos
        double p_supply = p->vdd * i_pmos;
        res.energy_total_joules += p_supply * dt;
        res.energy_sc_joules += (p->vdd * i_sc) * dt;

        t += dt;
    }

    res.energy_cap_joules = res.energy_total_joules - res.energy_sc_joules;
    return res;
}
