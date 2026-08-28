/* C99: Інженерний аналіз відриву потоку, примежового шару та вихорів Кармана */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define PI 3.14159265358979323846
#define THWAITES_SEP_LIMIT (-0.090)

typedef struct {
    double x;           /* координата вздовж стінки, м */
    double u_ext;       /* зовнішня швидкість U(x), м/с */
    double du_dx;       /* градієнт швидкості dU/dx, 1/с */
    double theta;       /* товщина втрати імпульсу θ, м */
    double delta_star;  /* товщина витіснення δ*, м */
    double h_shape;     /* форм-параметр H = δ*/θ */
    double lambda;      /* форм-параметр Твейтса λ */
    double tau_w;       /* дотичне напруження на стінці, Па */
    double cf;          /* локальний коефіцієнт тертя */
    bool is_inflection; /* наявність точки перегину */
} FlowStation;

typedef struct {
    double strouhal;    /* число Струхаля St */
    double frequency;   /* частота зриву вихорів f, Гц */
    double lift_amp;    /* амплітуда поперечної сили, Н/м */
    double drag_mean;   /* середній опір тиску, Н/м */
} KarmanVortexMetrics;

static inline double clamp_d(double val, double min_v, double max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

/* Форм-параметр H(λ) за кореляцією Твейтса — Джебеджі */
double calc_thwaites_h(double lam) {
    double l = clamp_d(lam, -0.090, 0.250);
    if (l < 0.0) {
        return 2.088 + 0.0731 / (l + 0.14);
    }
    return 2.61 - 3.75 * l + 5.24 * l * l;
}

/* Безрозмірна функція зсуву S(λ) */
double calc_thwaites_s(double lam) {
    double l = clamp_d(lam, -0.090, 0.250);
    return pow(l + 0.090, 0.62);
}

/* Інтегрування примежового шару методом Твейтса */
void analyze_boundary_layer(const double *x, const double *u, int n, 
                            double rho, double nu, FlowStation *out, 
                            int *sep_index, double *x_sep) {
    *sep_index = -1;
    *x_sep = -1.0;
    
    double *integral_u5 = (double*)calloc(n, sizeof(double));
    for (int i = 1; i < n; ++i) {
        double u_avg5 = 0.5 * (pow(u[i], 5.0) + pow(u[i - 1], 5.0));
        integral_u5[i] = integral_u5[i - 1] + u_avg5 * (x[i] - x[i - 1]);
    }
    
    for (int i = 0; i < n; ++i) {
        out[i].x = x[i];
        out[i].u_ext = u[i];
        
        /* Градієнт dU/dx за триточковою різницевою схемою */
        if (i == 0) {
            out[i].du_dx = (u[1] - u[0]) / (x[1] - x[0]);
        } else if (i == n - 1) {
            out[i].du_dx = (u[n - 1] - u[n - 2]) / (x[n - 1] - x[n - 2]);
        } else {
            double h1 = x[i] - x[i - 1];
            double h2 = x[i + 1] - x[i];
            out[i].du_dx = (h1 * h1 * u[i + 1] + (h2 * h2 - h1 * h1) * u[i] - h2 * h2 * u[i - 1]) /
                           (h1 * h2 * (h1 + h2));
        }
        
        /* Точка перегину існує, якщо градієнт тиску несприятливий (dU/dx < 0) */
        out[i].is_inflection = (out[i].du_dx < 0.0);
        
        double th2 = 0.0;
        if (u[i] > 1e-5) {
            th2 = (0.45 * nu * integral_u5[i]) / pow(u[i], 6.0);
        } else if (out[i].du_dx > 0.0) {
            th2 = 0.075 * nu / out[i].du_dx;
        }
        
        out[i].theta = sqrt(th2);
        out[i].lambda = (th2 / nu) * out[i].du_dx;
        out[i].h_shape = calc_thwaites_h(out[i].lambda);
        out[i].delta_star = out[i].h_shape * out[i].theta;
        
        double s_val = calc_thwaites_s(out[i].lambda);
        if (out[i].theta > 1e-9 && u[i] > 1e-5) {
            out[i].tau_w = (rho * nu * u[i] / out[i].theta) * s_val;
            out[i].cf = 2.0 * out[i].tau_w / (rho * u[i] * u[i]);
        } else {
            out[i].tau_w = 0.0;
            out[i].cf = 0.0;
        }
    }
    
    /* Пошук точки відриву λ = −0.090 */
    for (int i = 1; i < n; ++i) {
        if (out[i].lambda <= THWAITES_SEP_LIMIT && out[i - 1].lambda > THWAITES_SEP_LIMIT) {
            double frac = (THWAITES_SEP_LIMIT - out[i - 1].lambda) / 
                          (out[i].lambda - out[i - 1].lambda);
            *x_sep = out[i - 1].x + frac * (out[i].x - out[i - 1].x);
            *sep_index = i;
            break;
        }
    }
    
    free(integral_u5);
}

/* Розрахунок параметрів вихрової доріжки Кармана для поперечного тіла */
KarmanVortexMetrics calc_karman_shedding(double u_inf, double diameter, double rho, double reynolds) {
    KarmanVortexMetrics m;
    
    /* Емпірична залежність числа Струхаля від числа Рейнольдса для циліндра */
    if (reynolds < 250.0) {
        m.strouhal = 0.212 * (1.0 - 21.2 / reynolds);
    } else if (reynolds < 2.0e5) {
        m.strouhal = 0.198 * (1.0 - 19.7 / reynolds);
    } else {
        m.strouhal = 0.220;
    }
    
    m.frequency = m.strouhal * u_inf / diameter;
    
    /* Оцінка амплітуди знакозмінної підйомної сили та опору тиску */
    double dynamic_q = 0.5 * rho * u_inf * u_inf;
    double c_l_amp = 0.45; /* амплітудний коефіцієнт бічної сили */
    double c_d_mean = 1.15; /* коефіцієнт опору докритичного циліндра */
    
    m.lift_amp = c_l_amp * dynamic_q * diameter;
    m.drag_mean = c_d_mean * dynamic_q * diameter;
    return m;
}

int main(void) {
    const int N = 101;
    const double L = 1.0;
    const double U0 = 25.0;
    const double rho = 1.225;
    const double nu = 1.5e-5;
    
    double *x = (double*)malloc(N * sizeof(double));
    double *u = (double*)malloc(N * sizeof(double));
    FlowStation *res = (FlowStation*)malloc(N * sizeof(FlowStation));
    
    /* Профіль зовнішньої швидкості з лінійним гальмуванням: U(x) = U0·(1 − 0.5·x/L) */
    for (int i = 0; i < N; ++i) {
        x[i] = (double)i / (double)(N - 1) * 0.35 * L;
        u[i] = U0 * (1.0 - 0.5 * (x[i] / L));
    }
    
    int sep_idx;
    double x_sep;
    analyze_boundary_layer(x, u, N, rho, nu, res, &sep_idx, &x_sep);
    
    printf("=== Інженерний аналіз відриву примежового шару (C99) ===\n");
    printf("U_0 = %.1f м/с, L = %.2f м, В'язкість ν = %.2e м²/с\n\n", U0, L, nu);
    
    printf(" %-8s %-10s %-8s %-8s %-8s %-10s %-6s\n",
           "x, м", "U(x), м/с", "θ, мм", "H", "λ", "τ_w, Па", "Перегин");
    printf("------------------------------------------------------------------\n");
    for (int i = 0; i < N; i += 15) {
        printf(" %-8.4f %-10.3f %-8.4f %-8.3f %-8.4f %-10.4f %-6s\n",
               res[i].x, res[i].u_ext, res[i].theta * 1000.0,
               res[i].h_shape, res[i].lambda, res[i].tau_w,
               res[i].is_inflection ? "ТАК" : "НІ");
    }
    printf("------------------------------------------------------------------\n");
    
    if (sep_idx >= 0) {
        printf("ТОЧКА ВІДРИВУ ПОТОКУ: x_sep = %.4f м (x/L = %.4f)\n\n", x_sep, x_sep / L);
    } else {
        printf("Відриву не виявлено.\n\n");
    }
    
    /* Розрахунок параметрів вихороутворення за трубою діаметром 0.15 м */
    double D = 0.15;
    double re = U0 * D / nu;
    KarmanVortexMetrics vm = calc_karman_shedding(U0, D, rho, re);
    
    printf("=== Характеристики вихрової доріжки фон Кармана ===\n");
    printf("Тіло: циліндр діаметром D = %.3f м, Число Re = %.2e\n", D, re);
    printf("Число Струхаля St = %.4f\n", vm.strouhal);
    printf("Частота зриву вихорів f = %.2f Гц\n", vm.frequency);
    printf("Амплітуда бічної сили F_y = %.2f Н/м\n", vm.lift_amp);
    printf("Середній опір тиску F_x = %.2f Н/м\n", vm.drag_mean);
    
    free(x);
    free(u);
    free(res);
    return 0;
}
