/* calculation_clamping.c — розрахунок параметрів захисту від індуктивного викиду */
#include <stdio.h>
#include <math.h>

typedef struct {
    double v_dd;        /* Напруга живлення, В */
    double l_ind;       /* Індуктивність навантаження, Гн */
    double i_peak;      /* Струм перед вимиканням, А */
    double r_coil;      /* Активний опір котушки, Ом */
    double bv_dss;      /* Напруга лавини MOSFET, В */
    double v_tvs_clamp; /* Напруга обмеження TVS, В */
} CircuitParams;

typedef struct {
    double t_demag_sec; /* Час знеструмлення котушки, с */
    double energy_joules;/* Повна енергія розсіювання, Дж */
    double peak_power_w;/* Пікова розсіювана потужність, Вт */
} DemagResult;

/* Розрахунок режиму прямої лавини MOSFET */
DemagResult calc_avalanche_mode(const CircuitParams *p) {
    DemagResult res;
    double v_diff = p->bv_dss - p->v_dd;
    if (v_diff <= 0.0) {
        res.t_demag_sec = -1.0; /* Помилка: BV_DSS має бути більшим за V_DD */
        return res;
    }
    res.t_demag_sec = (p->l_ind * p->i_peak) / v_diff;
    res.energy_joules = 0.5 * p->l_ind * p->i_peak * p->i_peak * (p->bv_dss / v_diff);
    res.peak_power_w = p->bv_dss * p->i_peak;
    return res;
}

/* Розрахунок режиму захисту зворотним діодом */
DemagResult calc_freewheel_diode(const CircuitParams *p, double v_f) {
    DemagResult res;
    /* Спад струму за законом i(t) = I0 * exp(-t/tau), де tau = L/R. Час до спаду 99% струму ≈ 5*tau */
    double tau = p->l_ind / (p->r_coil > 0.05 ? p->r_coil : 0.05);
    res.t_demag_sec = 5.0 * tau;
    res.energy_joules = 0.5 * p->l_ind * p->i_peak * p->i_peak;
    res.peak_power_w = (p->v_dd + v_f) * p->i_peak;
    return res;
}

/* Розрахунок режиму захисту супресором (TVS) */
DemagResult calc_tvs_mode(const CircuitParams *p) {
    DemagResult res;
    double v_diff = p->v_tvs_clamp - p->v_dd;
    if (v_diff <= 0.0) {
        res.t_demag_sec = -1.0;
        return res;
    }
    res.t_demag_sec = (p->l_ind * p->i_peak) / v_diff;
    res.energy_joules = 0.5 * p->l_ind * p->i_peak * p->i_peak * (p->v_tvs_clamp / v_diff);
    res.peak_power_w = p->v_tvs_clamp * p->i_peak;
    return res;
}
