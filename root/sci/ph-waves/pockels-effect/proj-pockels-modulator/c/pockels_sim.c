/* pockels_sim.c - Чисельне моделювання комірки Поккельса мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double real;
    double imag;
} complex_d;

static complex_d c_make(double r, double i) {
    complex_d c = {r, i};
    return c;
}

static complex_d c_exp_i(double phi) {
    return c_make(cos(phi), sin(phi));
}

static complex_d c_mul(complex_d a, complex_d b) {
    return c_make(a.real * b.real - a.imag * b.imag,
                  a.real * b.imag + a.imag * b.real);
}

static complex_d c_add(complex_d a, complex_d b) {
    return c_make(a.real + b.real, a.imag + b.imag);
}

static double c_abs_sq(complex_d c) {
    return c.real * c.real + c.imag * c.imag;
}

typedef struct {
    complex_d ex;
    complex_d ey;
} jones_vector_t;

typedef struct {
    double v_pi;          /* Напівхвильова напруга (Вольт) */
    double wavelength_m;  /* Довжина хвилі (метрів) */
    double length_m;      /* Довжина кристала (метрів) */
    double dn_dt;         /* Термооптичний коефіцієнт (1/K) */
    double temp_ref;      /* Базова температура (°C) */
} pockels_config_t;

/* Обчислення фазового набігу */
double pockels_calc_retardation(const pockels_config_t* cfg, double v_applied, double temp_c) {
    double gamma_v = M_PI * (v_applied / cfg->v_pi);
    double dt = temp_c - cfg->temp_ref;
    double gamma_t = (2.0 * M_PI / cfg->wavelength_m) * cfg->dn_dt * cfg->length_m * dt;
    return gamma_v + gamma_t;
}

/* Проходження вектора Джонса крізь модулятор */
jones_vector_t pockels_transform(const pockels_config_t* cfg, jones_vector_t in, double v_applied, double temp_c) {
    double gamma = pockels_calc_retardation(cfg, v_applied, temp_c);
    
    /* 1. Поляризатор P1 під 45° */
    complex_d sum1 = c_add(in.ex, in.ey);
    jones_vector_t p1_out = {
        c_make(0.5 * sum1.real, 0.5 * sum1.imag),
        c_make(0.5 * sum1.real, 0.5 * sum1.imag)
    };

    /* 2. Комірка Поккельса (фазовий зсув gamma) */
    complex_d phase_x = c_exp_i(-0.5 * gamma);
    complex_d phase_y = c_exp_i(0.5 * gamma);
    jones_vector_t pc_out = {
        c_mul(p1_out.ex, phase_x),
        c_mul(p1_out.ey, phase_y)
    };

    /* 3. Аналізатор P2 під -45° (різниця компонентів) */
    complex_d diff = c_make(pc_out.ex.real - pc_out.ey.real, pc_out.ex.imag - pc_out.ey.imag);
    jones_vector_t out = {
        c_make(0.5 * diff.real, 0.5 * diff.imag),
        c_make(-0.5 * diff.real, -0.5 * diff.imag)
    };

    return out;
}

/* Обчислення вихідної інтенсивності */
double pockels_calc_intensity(jones_vector_t v) {
    return c_abs_sq(v.ex) + c_abs_sq(v.ey);
}

int main(void) {
    pockels_config_t cfg = {
        .v_pi = 300.0,            /* V_pi = 300 V (поперечна LiNbO3) */
        .wavelength_m = 1550e-9,  /* 1550 нм */
        .length_m = 0.02,         /* 20 мм */
        .dn_dt = 3.9e-5,          /* LiNbO3 dn/dT */
        .temp_ref = 25.0
    };

    printf("=== МОДЕЛЬ КОРЕКЦІЇ РОБОЧОЇ ТОЧКИ КОМІРКИ ПОККЕЛЬСА (C) ===\n");
    printf("Напівхвильова напруга V_pi = %.1f В, Довжина хвилі = %.0f нм\n\n", cfg.v_pi, cfg.wavelength_m * 1e9);

    jones_vector_t in_beam = { c_make(1.0, 0.0), c_make(0.0, 0.0) };
    double bias_v = cfg.v_pi / 2.0; /* Квадратурна точка V_pi / 2 = 150 V */

    printf(" V_applied (V) | Temp (°C) | Retardation (rad) | Intensity (I/I0) \n");
    printf("---------------+-----------+-------------------+------------------\n");

    double test_voltages[] = {0.0, bias_v, cfg.v_pi, 1.5 * cfg.v_pi, 2.0 * cfg.v_pi};
    for (int i = 0; i < 5; ++i) {
        double v = test_voltages[i];
        double gamma = pockels_calc_retardation(&cfg, v, 25.0);
        jones_vector_t out_beam = pockels_transform(&cfg, in_beam, v, 25.0);
        double intensity = pockels_calc_intensity(out_beam);

        printf("   %7.1f     |   %5.1f   |     %9.4f     |    %8.4f\n",
               v, 25.0, gamma, intensity);
    }

    printf("\nВплив температурного дрейфу при V = V_bias (150 V):\n");
    double temps[] = {20.0, 25.0, 30.0, 35.0};
    for (int i = 0; i < 4; ++i) {
        double t = temps[i];
        double gamma = pockels_calc_retardation(&cfg, bias_v, t);
        jones_vector_t out_beam = pockels_transform(&cfg, in_beam, bias_v, t);
        double intensity = pockels_calc_intensity(out_beam);

        printf("   T = %.1f °C | Gamma = %.4f rad | Intensity = %.4f\n", t, gamma, intensity);
    }

    return 0;
}
