/* C99: Чисельний розв'язувач Твейтса та тестовий набір */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define LAM_SEP (-0.090)
#define LAM_MAX   0.250
#define PI 3.14159265358979323846

typedef struct {
    double *theta;      /* товщина втрати імпульсу θ, м */
    double *delta_star; /* товщина витіснення δ*, м */
    double *cf;         /* коефіцієнт тертя c_f */
    double *lam;        /* параметр Твейтса λ */
    double *re_theta;   /* число Рейнольдса Re_θ */
    bool is_separated;
    double s_sep;       /* координата відриву, м */
    int n;
} ThwaitesMarchResult;

static inline double clamp_lam(double l) {
    if (l < LAM_SEP) return LAM_SEP;
    if (l > LAM_MAX) return LAM_MAX;
    return l;
}

static inline double thwaites_shear_factor(double l) {
    double lc = clamp_lam(l);
    return pow(lc - LAM_SEP, 0.62);
}

static inline double thwaites_shape_factor(double l) {
    double lc = clamp_lam(l);
    if (lc < 0.0) {
        return 2.088 + 0.0731 / (lc + 0.14);
    }
    return 2.61 - 3.75 * lc + 5.24 * lc * lc;
}

static inline double pow5(double v) {
    double v2 = v * v;
    return v2 * v2 * v;
}

static inline double pow6(double v) {
    double v3 = v * v * v;
    return v3 * v3;
}

void compute_velocity_slope(int n, const double *s, const double *u, double *du_ds) {
    for (int i = 1; i < n - 1; ++i) {
        double h1 = s[i] - s[i - 1];
        double h2 = s[i + 1] - s[i];
        du_ds[i] = (h1 * h1 * u[i + 1] + (h2 * h2 - h1 * h1) * u[i] - h2 * h2 * u[i - 1]) /
                   (h1 * h2 * (h1 + h2));
    }
    du_ds[0] = (u[1] - u[0]) / (s[1] - s[0]);
    du_ds[n - 1] = (u[n - 1] - u[n - 2]) / (s[n - 1] - s[n - 2]);
}

ThwaitesMarchResult* run_thwaites_march(int n, const double *s, const double *u, 
                                        double nu, double theta0) {
    ThwaitesMarchResult *res = (ThwaitesMarchResult*)malloc(sizeof(ThwaitesMarchResult));
    res->n = n;
    res->theta = (double*)malloc(n * sizeof(double));
    res->delta_star = (double*)malloc(n * sizeof(double));
    res->cf = (double*)malloc(n * sizeof(double));
    res->lam = (double*)malloc(n * sizeof(double));
    res->re_theta = (double*)malloc(n * sizeof(double));
    res->is_separated = false;
    res->s_sep = -1.0;

    double *du_ds = (double*)malloc(n * sizeof(double));
    compute_velocity_slope(n, s, u, du_ds);

    double *integral_u5 = (double*)calloc(n, sizeof(double));
    for (int i = 1; i < n; ++i) {
        double avg5 = 0.5 * (pow5(u[i]) + pow5(u[i - 1]));
        integral_u5[i] = integral_u5[i - 1] + avg5 * (s[i] - s[i - 1]);
    }

    double seed = theta0 * theta0 * pow6(u[0]);
    for (int i = 0; i < n; ++i) {
        double th2 = 0.0;
        if (u[i] > 1e-6) {
            th2 = (0.45 * nu * integral_u5[i] + seed) / pow6(u[i]);
        } else if (du_ds[i] > 0.0) {
            th2 = 0.075 * nu / du_ds[i];
        }

        res->theta[i] = sqrt(th2);
        res->lam[i] = (th2 / nu) * du_ds[i];
        res->delta_star[i] = thwaites_shape_factor(res->lam[i]) * res->theta[i];
        if (u[i] * res->theta[i] > 1e-9) {
            res->cf[i] = 2.0 * nu * thwaites_shear_factor(res->lam[i]) / (u[i] * res->theta[i]);
        } else {
            res->cf[i] = 0.0;
        }
        res->re_theta[i] = u[i] * res->theta[i] / nu;
    }

    for (int i = 1; i < n; ++i) {
        if (res->lam[i] <= LAM_SEP && res->lam[i - 1] > LAM_SEP) {
            double factor = (LAM_SEP - res->lam[i - 1]) / (res->lam[i] - res->lam[i - 1]);
            res->s_sep = s[i - 1] + factor * (s[i] - s[i - 1]);
            res->is_separated = true;
            break;
        }
    }

    free(du_ds);
    free(integral_u5);
    return res;
}

void free_thwaites_result(ThwaitesMarchResult *r) {
    if (!r) return;
    free(r->theta);
    free(r->delta_star);
    free(r->cf);
    free(r->lam);
    free(r->re_theta);
    free(r);
}

void run_howarth_validation(void) {
    double nu = 1.5e-5, u0 = 20.0, l = 1.0;
    int n = 201;
    double *s = (double*)malloc(n * sizeof(double));
    double *u = (double*)malloc(n * sizeof(double));
    for (int i = 0; i < n; ++i) {
        s[i] = 0.15 * l * (double)i / (double)(n - 1);
        u[i] = u0 * (1.0 - s[i] / l);
    }
    ThwaitesMarchResult *r = run_thwaites_march(n, s, u, nu, 0.0);
    printf("1. Течія Говарта U = U0*(1 - x/L):\n");
    if (r->is_separated) {
        printf("   Відрив на x/L = %.4f (точний розв'язок = 0.1198, похибка = +%.1f%%)\n",
               r->s_sep / l, (r->s_sep / l - 0.1198) / 0.1198 * 100.0);
    }
    free_thwaites_result(r);
    free(s);
    free(u);
}

void run_tani_validation(void) {
    double nu = 1.5e-5, u0 = 20.0, l = 1.0;
    int n = 301;
    double *s = (double*)malloc(n * sizeof(double));
    double *u = (double*)malloc(n * sizeof(double));
    for (int i = 0; i < n; ++i) {
        s[i] = 0.35 * l * (double)i / (double)(n - 1);
        double xi = s[i] / l;
        u[i] = u0 * (1.0 - xi * xi);
    }
    ThwaitesMarchResult *r = run_thwaites_march(n, s, u, nu, 0.0);
    printf("2. Течія Тані U = U0*(1 - (x/L)^2):\n");
    if (r->is_separated) {
        printf("   Відрив на x/L = %.4f (точний розв'язок = 0.2710, похибка = +%.1f%%)\n",
               r->s_sep / l, (r->s_sep / l - 0.2710) / 0.2710 * 100.0);
    }
    free_thwaites_result(r);
    free(s);
    free(u);
}

void run_cylinder_validation(void) {
    double nu = 1.5e-5, u_inf = 10.0, radius = 0.5;
    int n = 361;
    double *s = (double*)malloc(n * sizeof(double));
    double *u = (double*)malloc(n * sizeof(double));
    for (int i = 0; i < n; ++i) {
        double phi = (PI * (double)i / (double)(n - 1));
        s[i] = radius * phi;
        u[i] = 2.0 * u_inf * sin(phi);
    }
    ThwaitesMarchResult *r = run_thwaites_march(n, s, u, nu, 0.0);
    printf("3. Нев'язке обтікання циліндра U = 2*U_inf*sin(phi):\n");
    if (r->is_separated) {
        double phi_sep_deg = (r->s_sep / radius) * 180.0 / PI;
        printf("   Відрив при phi = %.2f deg (потенційна крива дає 103.1 deg)\n", phi_sep_deg);
    }
    free_thwaites_result(r);
    free(s);
    free(u);
}

int main(void) {
    printf("=== Чисельне тестування інтегрального методу Твейтса (C99) ===\n\n");
    run_howarth_validation();
    run_tani_validation();
    run_cylinder_validation();
    return 0;
}
