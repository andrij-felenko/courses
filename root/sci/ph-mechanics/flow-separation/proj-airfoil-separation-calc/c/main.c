/* C99: Модуль розрахунку примежового шару методом Твейтса на профілях NACA */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define THWAITES_LAM_SEP (-0.090)
#define THWAITES_LAM_MAX   0.250
#define PI 3.14159265358979323846

typedef struct {
    double m;     /* максимальний кембер (наприклад, 0.02 для NACA 2412) */
    double p;     /* координата максимуму кембера (0.4) */
    double t;     /* відносна товщина (0.12) */
    double chord; /* хорда, м */
} NacaAirfoil;

typedef struct {
    int n_points;
    double *x;          /* хордова координата x, м */
    double *y;          /* вертикальна координата верхньої поверхні y_u, м */
    double *s;          /* дугова довжина від носка, м */
    double *u_ext;      /* зовнішня швидкість U(s), м/с */
    double *du_ds;      /* градієнт швидкості dU/ds, 1/с */
    double *theta;      /* товщина втрати імпульсу θ, м */
    double *delta_star; /* товщина витіснення δ*, м */
    double *h_shape;    /* форм-параметр H = δ*/θ */
    double *lambda;     /* параметр Твейтса λ */
    double *cf;         /* коефіцієнт тертя c_f */
    double *re_theta;   /* число Рейнольдса Re_θ */
    
    /* Параметри профілю Польгаузена для порівняння */
    double *delta_pohl; /* повна товщина шару Польгаузена δ, м */
    double *lambda_pohl;/* форм-параметр Польгаузена Λ */
    double *cf_pohl;    /* тертя Польгаузена c_f */
    
    bool is_separated;
    double s_separation; /* дуга відриву Твейтса, м */
    double x_separation; /* координата x відриву Твейтса, м */
    
    bool is_pohl_separated;
    double x_pohl_separation; /* координата відриву Польгаузена (Λ = -12) */
    
    bool is_transitioned;
    double s_transition; /* дуга переходу Мішеля, м */
} BoundaryLayerResult;

static inline double clamp_val(double val, double low, double high) {
    if (val < low) return low;
    if (val > high) return high;
    return val;
}

static inline double thwaites_shear(double lam) {
    double l_clip = clamp_val(lam, THWAITES_LAM_SEP, THWAITES_LAM_MAX);
    return pow(l_clip - THWAITES_LAM_SEP, 0.62);
}

static inline double thwaites_shape(double lam) {
    double l_clip = clamp_val(lam, THWAITES_LAM_SEP, THWAITES_LAM_MAX);
    if (l_clip < 0.0) {
        return 2.088 + 0.0731 / (l_clip + 0.14);
    }
    return 2.61 - 3.75 * l_clip + 5.24 * l_clip * l_clip;
}

static inline double michel_re_theta_crit(double re_s) {
    if (re_s < 100.0) return 1e9;
    return 1.174 * (1.0 + 22400.0 / re_s) * pow(re_s, 0.46);
}

/* Розрахунок геометрії та розподілу швидкості NACA */
void generate_naca_suction_side(const NacaAirfoil *foil, double alpha_deg, double u_inf,
                                int n, double *x_out, double *y_out, double *s_out, double *u_out) {
    double alpha = alpha_deg * PI / 180.0;
    double c = foil->chord;
    
    /* Косинусна розбивка для згущення вузлів біля носка */
    for (int i = 0; i < n; ++i) {
        double beta = PI * (double)i / (double)(n - 1);
        double xc = 0.5 * (1.0 - cos(beta));
        
        double yc = 0.0;
        double dyc_dx = 0.0;
        if (foil->p > 0.0 && foil->m > 0.0) {
            if (xc < foil->p) {
                yc = (foil->m / (foil->p * foil->p)) * (2.0 * foil->p * xc - xc * xc);
                dyc_dx = (2.0 * foil->m / (foil->p * foil->p)) * (foil->p - xc);
            } else {
                double p1 = 1.0 - foil->p;
                yc = (foil->m / (p1 * p1)) * ((1.0 - 2.0 * foil->p) + 2.0 * foil->p * xc - xc * xc);
                dyc_dx = (2.0 * foil->m / (p1 * p1)) * (foil->p - xc);
            }
        }
        double theta_c = atan(dyc_dx);
        
        double yt = 5.0 * foil->t * (0.2969 * sqrt(xc) - 0.1260 * xc - 
                                     0.3516 * xc * xc + 0.2843 * xc * xc * xc - 
                                     0.1015 * xc * xc * xc * xc);
        
        x_out[i] = (xc - yt * sin(theta_c)) * c;
        y_out[i] = (yc + yt * cos(theta_c)) * c;
        
        double v_ratio;
        if (xc < 1e-6) {
            v_ratio = 0.0;
        } else {
            double thickness_factor = 1.0 + 1.2 * foil->t * (1.0 - xc);
            double camber_factor = 1.0 + 2.5 * foil->m * sin(PI * xc);
            double alpha_lift = 2.0 * sin(alpha + 2.0 * foil->m) * sqrt((1.0 - xc) / (xc + 0.005));
            v_ratio = (cos(alpha) * thickness_factor * camber_factor + alpha_lift);
            if (v_ratio < 0.0) v_ratio = 0.0;
        }
        u_out[i] = u_inf * v_ratio;
    }
    
    s_out[0] = 0.0;
    for (int i = 1; i < n; ++i) {
        double dx = x_out[i] - x_out[i - 1];
        double dy = y_out[i] - y_out[i - 1];
        s_out[i] = s_out[i - 1] + sqrt(dx * dx + dy * dy);
    }
}

void compute_gradient(int n, const double *s, const double *u, double *du_ds) {
    for (int i = 1; i < n - 1; ++i) {
        double h1 = s[i] - s[i - 1];
        double h2 = s[i + 1] - s[i];
        du_ds[i] = (h1 * h1 * u[i + 1] + (h2 * h2 - h1 * h1) * u[i] - h2 * h2 * u[i - 1]) /
                   (h1 * h2 * (h1 + h2));
    }
    du_ds[0] = (u[1] - u[0]) / (s[1] - s[0]);
    du_ds[n - 1] = (u[n - 1] - u[n - 2]) / (s[n - 1] - s[n - 2]);
}

BoundaryLayerResult* run_thwaites_solver(const NacaAirfoil *foil, double alpha_deg, 
                                        double u_inf, double nu, int n) {
    BoundaryLayerResult *res = (BoundaryLayerResult*)malloc(sizeof(BoundaryLayerResult));
    res->n_points = n;
    res->x = (double*)malloc(n * sizeof(double));
    res->y = (double*)malloc(n * sizeof(double));
    res->s = (double*)malloc(n * sizeof(double));
    res->u_ext = (double*)malloc(n * sizeof(double));
    res->du_ds = (double*)malloc(n * sizeof(double));
    res->theta = (double*)malloc(n * sizeof(double));
    res->delta_star = (double*)malloc(n * sizeof(double));
    res->h_shape = (double*)malloc(n * sizeof(double));
    res->lambda = (double*)malloc(n * sizeof(double));
    res->cf = (double*)malloc(n * sizeof(double));
    res->re_theta = (double*)malloc(n * sizeof(double));
    res->delta_pohl = (double*)malloc(n * sizeof(double));
    res->lambda_pohl = (double*)malloc(n * sizeof(double));
    res->cf_pohl = (double*)malloc(n * sizeof(double));
    res->is_separated = false;
    res->is_pohl_separated = false;
    res->is_transitioned = false;
    res->s_separation = -1.0;
    res->x_separation = -1.0;
    res->x_pohl_separation = -1.0;
    res->s_transition = -1.0;
    
    generate_naca_suction_side(foil, alpha_deg, u_inf, n, res->x, res->y, res->s, res->u_ext);
    compute_gradient(n, res->s, res->u_ext, res->du_ds);
    
    double *integral_u5 = (double*)calloc(n, sizeof(double));
    for (int i = 1; i < n; ++i) {
        double u_avg5 = 0.5 * (pow(res->u_ext[i], 5.0) + pow(res->u_ext[i - 1], 5.0));
        integral_u5[i] = integral_u5[i - 1] + u_avg5 * (res->s[i] - res->s[i - 1]);
    }
    
    for (int i = 0; i < n; ++i) {
        double u = res->u_ext[i];
        double du = res->du_ds[i];
        double th2 = 0.0;
        
        if (u > 1e-4) {
            th2 = (0.45 * nu * integral_u5[i]) / pow(u, 6.0);
        } else if (du > 0.0) {
            th2 = 0.075 * nu / du;
        }
        
        res->theta[i] = sqrt(th2);
        res->lambda[i] = (th2 / nu) * du;
        res->h_shape[i] = thwaites_shape(res->lambda[i]);
        res->delta_star[i] = res->h_shape[i] * res->theta[i];
        
        if (u * res->theta[i] > 1e-9) {
            res->cf[i] = 2.0 * nu * thwaites_shear(res->lambda[i]) / (u * res->theta[i]);
        } else {
            res->cf[i] = 0.0;
        }
        res->re_theta[i] = u * res->theta[i] / nu;
        
        /* Розрахунок параметрів Польгаузена: δ ≈ θ / 0.117 */
        res->delta_pohl[i] = res->theta[i] / 0.11746;
        res->lambda_pohl[i] = (res->delta_pohl[i] * res->delta_pohl[i] / nu) * du;
        if (u * res->delta_pohl[i] > 1e-9) {
            double pohl_factor = 2.0 + res->lambda_pohl[i] / 6.0;
            if (pohl_factor < 0.0) pohl_factor = 0.0;
            res->cf_pohl[i] = 2.0 * (nu / (u * res->delta_pohl[i])) * pohl_factor;
        } else {
            res->cf_pohl[i] = 0.0;
        }
        
        if (!res->is_transitioned && i > 0) {
            double re_s = u * res->s[i] / nu;
            double re_th_crit = michel_re_theta_crit(re_s);
            if (res->re_theta[i] >= re_th_crit) {
                res->is_transitioned = true;
                res->s_transition = res->s[i];
            }
        }
    }
    
    /* Локалізація відриву Твейтса (λ = -0.090) */
    for (int i = 1; i < n; ++i) {
        if (res->lambda[i] <= THWAITES_LAM_SEP && res->lambda[i - 1] > THWAITES_LAM_SEP) {
            double factor = (THWAITES_LAM_SEP - res->lambda[i - 1]) / 
                            (res->lambda[i] - res->lambda[i - 1]);
            res->s_separation = res->s[i - 1] + factor * (res->s[i] - res->s[i - 1]);
            res->x_separation = res->x[i - 1] + factor * (res->x[i] - res->x[i - 1]);
            res->is_separated = true;
            break;
        }
    }
    
    /* Локалізація відриву Польгаузена (Λ = -12.0) */
    for (int i = 1; i < n; ++i) {
        if (res->lambda_pohl[i] <= -12.0 && res->lambda_pohl[i - 1] > -12.0) {
            double factor = (-12.0 - res->lambda_pohl[i - 1]) / 
                            (res->lambda_pohl[i] - res->lambda_pohl[i - 1]);
            res->x_pohl_separation = res->x[i - 1] + factor * (res->x[i] - res->x[i - 1]);
            res->is_pohl_separated = true;
            break;
        }
    }
    
    free(integral_u5);
    return res;
}

void free_boundary_layer_result(BoundaryLayerResult *res) {
    if (!res) return;
    free(res->x);
    free(res->y);
    free(res->s);
    free(res->u_ext);
    free(res->du_ds);
    free(res->theta);
    free(res->delta_star);
    free(res->h_shape);
    free(res->lambda);
    free(res->cf);
    free(res->re_theta);
    free(res->delta_pohl);
    free(res->lambda_pohl);
    free(res->cf_pohl);
    free(res);
}

void run_profile_test_suite(void) {
    double nu = 1.5e-5;
    double u_inf = 30.0;
    int n_nodes = 161;
    
    NacaAirfoil foils[3] = {
        { .m = 0.00, .p = 0.0, .t = 0.12, .chord = 1.0 }, /* NACA 0012 */
        { .m = 0.02, .p = 0.4, .t = 0.12, .chord = 1.0 }, /* NACA 2412 */
        { .m = 0.04, .p = 0.4, .t = 0.12, .chord = 1.0 }  /* NACA 4412 */
    };
    const char *names[3] = { "NACA 0012", "NACA 2412", "NACA 4412" };
    double angles[3] = { 0.0, 4.0, 8.0 };
    
    printf("=== Зведена таблиця розрахунків Твейтса для профілів NACA ===\n");
    printf("%-10s %-8s %-12s %-12s %-10s %-12s\n",
           "Профіль", "Alpha", "x_sep/c (Thw)", "x_sep/c (Pohl)", "θ_sep, мм", "Re_θ,sep");
    printf("-------------------------------------------------------------------------\n");
    
    for (int f = 0; f < 3; ++f) {
        for (int a = 0; a < 3; ++a) {
            BoundaryLayerResult *r = run_thwaites_solver(&foils[f], angles[a], u_inf, nu, n_nodes);
            double x_thw = r->is_separated ? (r->x_separation / foils[f].chord) : 1.0;
            double x_poh = r->is_pohl_separated ? (r->x_pohl_separation / foils[f].chord) : 1.0;
            
            double th_sep = 0.0, re_th = 0.0;
            for (int i = 0; i < n_nodes; ++i) {
                if (r->x[i] >= r->x_separation) {
                    th_sep = r->theta[i] * 1000.0;
                    re_th = r->re_theta[i];
                    break;
                }
            }
            printf("%-10s %-8.1f %-12.4f %-12.4f %-10.4f %-12.1f\n",
                   names[f], angles[a], x_thw, x_poh, th_sep, re_th);
            free_boundary_layer_result(r);
        }
    }
    printf("-------------------------------------------------------------------------\n\n");
}

void run_mesh_refinement_test(void) {
    NacaAirfoil foil = { .m = 0.02, .p = 0.4, .t = 0.12, .chord = 1.0 };
    double u_inf = 30.0, nu = 1.5e-5, alpha = 4.0;
    int meshes[5] = { 41, 81, 161, 321, 641 };
    
    printf("=== Дослідження сіткової збіжності для NACA 2412 (Alpha = 4.0 deg) ===\n");
    printf(" %-8s %-14s %-14s %-12s\n", "Вузлів", "x_sep/c", "s_sep, м", "θ_sep, мм");
    printf("----------------------------------------------------\n");
    
    for (int i = 0; i < 5; ++i) {
        BoundaryLayerResult *r = run_thwaites_solver(&foil, alpha, u_inf, nu, meshes[i]);
        double th_sep = 0.0;
        for (int k = 0; k < meshes[i]; ++k) {
            if (r->x[k] >= r->x_separation) {
                th_sep = r->theta[k] * 1000.0;
                break;
            }
        }
        printf(" %-8d %-14.5f %-14.5f %-12.5f\n",
               meshes[i], r->x_separation / foil.chord, r->s_separation, th_sep);
        free_boundary_layer_result(r);
    }
    printf("----------------------------------------------------\n\n");
}

int main(void) {
    NacaAirfoil foil = { .m = 0.02, .p = 0.4, .t = 0.12, .chord = 1.0 }; /* NACA 2412 */
    double u_inf = 30.0;
    double nu = 1.5e-5;
    double alpha = 4.0;
    int n_nodes = 161;
    
    printf("=== Розрахунок примежового шару методом Твейтса (C99) ===\n");
    printf("Профіль: NACA 2412, Хорда c = %.2f м, U_inf = %.1f м/с, Alpha = %.1f deg\n", 
           foil.chord, u_inf, alpha);
    printf("Число Рейнольдса Re_c = %.2e\n\n", u_inf * foil.chord / nu);
    
    BoundaryLayerResult *r = run_thwaites_solver(&foil, alpha, u_inf, nu, n_nodes);
    
    printf(" %-8s %-8s %-10s %-10s %-8s %-8s %-10s %-8s\n",
           "x/c", "s/c", "U, м/с", "θ, мм", "H", "λ", "c_f·10³", "Re_θ");
    printf("-------------------------------------------------------------------------\n");
    
    int step = n_nodes / 16;
    for (int i = 0; i < n_nodes; i += step) {
        printf(" %-8.4f %-8.4f %-10.3f %-10.4f %-8.3f %-8.4f %-10.4f %-8.1f\n",
               r->x[i] / foil.chord, r->s[i] / foil.chord, r->u_ext[i],
               r->theta[i] * 1000.0, r->h_shape[i], r->lambda[i],
               r->cf[i] * 1000.0, r->re_theta[i]);
    }
    printf("-------------------------------------------------------------------------\n");
    
    if (r->is_separated) {
        printf("Ламінарний відрив потоку (Твейтс): x_sep/c = %.4f (s_sep = %.4f м)\n",
               r->x_separation / foil.chord, r->s_separation);
    }
    if (r->is_pohl_separated) {
        printf("Ламінарний відрив за Польгаузеном:  x_sep/c = %.4f (Λ = -12.0)\n",
               r->x_pohl_separation / foil.chord);
    }
    if (r->is_transitioned) {
        printf("Перехід Мішеля Re_θ ≥ Re_θ,tr: s_tr = %.4f м\n\n", r->s_transition);
    }
    
    free_boundary_layer_result(r);
    
    run_profile_test_suite();
    run_mesh_refinement_test();
    return 0;
}
