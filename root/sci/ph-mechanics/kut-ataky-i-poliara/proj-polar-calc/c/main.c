#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define MAX_POLAR_POINTS 128

typedef struct {
    double alpha_deg; /* Кут атаки (градуси) */
    double cl;        /* Коефіцієнт підйомної сили */
    double cd;        /* Коефіцієнт лобового опору */
    double cm;        /* Коефіцієнт поздовжнього моменту відносно c/4 */
} PolarPoint;

typedef struct {
    PolarPoint points[MAX_POLAR_POINTS];
    size_t count;
    double reynolds_base; /* Базове число Re таблиці */
} AirfoilPolar;

typedef struct {
    double alpha_zero_lift_deg; /* Кут нульової сили alpha_0 */
    double alpha_crit_deg;      /* Критичний кут атаки alpha_crit */
    double cl_max;              /* Максимальний C_L */
    double cd_min;              /* Мінімальний опір C_D,min */
    
    /* Найвигідніший режим (максимальна якість) */
    double k_max;               /* Максимальна якість K = C_L / C_D */
    double alpha_k_max_deg;
    double cl_at_k_max;
    double cd_at_k_max;

    /* Економічний режим (мінімальна потужність двигуна) */
    double e_max;               /* Максимум C_L^(1.5) / C_D */
    double alpha_e_max_deg;
    
    /* Швидкісний режим */
    double j_max;               /* Максимум C_L^(0.5) / C_D */
    double alpha_j_max_deg;
} PolarMetrics;

/* Лінійна інтерполяція значень поляри */
static bool polar_evaluate(const AirfoilPolar* p, double alpha_deg, PolarPoint* out) {
    if (!p || p->count < 2 || !out) return false;
    if (alpha_deg < p->points[0].alpha_deg || alpha_deg > p->points[p->count - 1].alpha_deg) {
        return false; /* За межами таблиці екстраполяція небезпечна */
    }
    for (size_t i = 0; i < p->count - 1; ++i) {
        if (alpha_deg >= p->points[i].alpha_deg && alpha_deg <= p->points[i + 1].alpha_deg) {
            double span = p->points[i + 1].alpha_deg - p->points[i].alpha_deg;
            double t = (span > 1e-9) ? (alpha_deg - p->points[i].alpha_deg) / span : 0.0;
            out->alpha_deg = alpha_deg;
            out->cl = p->points[i].cl + t * (p->points[i + 1].cl - p->points[i].cl);
            out->cd = p->points[i].cd + t * (p->points[i + 1].cd - p->points[i].cd);
            out->cm = p->points[i].cm + t * (p->points[i + 1].cm - p->points[i].cm);
            return true;
        }
    }
    return false;
}

/* Розрахунок характеристик поляри */
bool polar_analyze(const AirfoilPolar* p, PolarMetrics* out) {
    if (!p || p->count < 3 || !out) return false;

    out->cl_max = -1e9;
    out->cd_min = 1e9;
    out->k_max = -1e9;
    out->e_max = -1e9;
    out->j_max = -1e9;
    out->alpha_zero_lift_deg = 0.0;

    bool found_zero_lift = false;

    for (size_t i = 0; i < p->count; ++i) {
        const PolarPoint* pt = &p->points[i];

        /* Пошук CL_max */
        if (pt->cl > out->cl_max) {
            out->cl_max = pt->cl;
            out->alpha_crit_deg = pt->alpha_deg;
        }

        /* Пошук CD_min */
        if (pt->cd < out->cd_min) {
            out->cd_min = pt->cd;
        }

        /* Пошук alpha_0 (перехід через нуль) */
        if (i > 0 && !found_zero_lift) {
            double prev_cl = p->points[i - 1].cl;
            if ((prev_cl <= 0.0 && pt->cl >= 0.0) || (prev_cl >= 0.0 && pt->cl <= 0.0)) {
                double t = -prev_cl / (pt->cl - prev_cl + 1e-12);
                out->alpha_zero_lift_deg = p->points[i - 1].alpha_deg + t * (pt->alpha_deg - p->points[i - 1].alpha_deg);
                found_zero_lift = true;
            }
        }

        /* Дотичні поляри (лише для додатного CL та CD > 0) */
        if (pt->cl > 0.001 && pt->cd > 0.0001) {
            double k = pt->cl / pt->cd;
            if (k > out->k_max) {
                out->k_max = k;
                out->alpha_k_max_deg = pt->alpha_deg;
                out->cl_at_k_max = pt->cl;
                out->cd_at_k_max = pt->cd;
            }

            double e = pow(pt->cl, 1.5) / pt->cd;
            if (e > out->e_max) {
                out->e_max = e;
                out->alpha_e_max_deg = pt->alpha_deg;
            }

            double j = sqrt(pt->cl) / pt->cd;
            if (j > out->j_max) {
                out->j_max = j;
                out->alpha_j_max_deg = pt->alpha_deg;
            }
        }
    }
    return true;
}

/* Обчислення центру тиску (у частках хорди) */
bool calculate_center_of_pressure(double cl, double cm_c4, double* x_cp_c) {
    if (!x_cp_c) return false;
    if (fabs(cl) < 0.02) {
        return false; /* Невизначеність: ділення на нуль */
    }
    /* x_cp = x_ac - c * (cm / cl), де x_ac = 0.25c */
    *x_cp_c = 0.25 - (cm_c4 / cl);
    return true;
}

/* Масштабування опору для низьких чисел Рейнольдса дронів */
double scale_cd_for_reynolds(double cd_base, double re_base, double re_target) {
    if (re_target <= 1000.0 || re_base <= 1000.0) return cd_base;
    
    /* Масштабування ламінарно-турбулентного тертя */
    double scale = pow(re_base / re_target, 0.20);
    double cd_scaled = cd_base * scale;

    /* Штраф на ламінарну бульбашку відриву (LSB) при Re < 10^5 */
    if (re_target < 100000.0) {
        double lsb_factor = (100000.0 - re_target) / 100000.0;
        cd_scaled += 0.015 * lsb_factor * lsb_factor;
    }
    return cd_scaled;
}
