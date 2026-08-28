#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура конфігурації оптичної системи */
typedef struct {
    double n1;          /* показник заломлення першого середовища (скло) */
    double n2;          /* показник заломлення зазору (повітря) */
    double n3;          /* показник заломлення третього середовища (скло) */
    double lambda_nm;   /* довжина хвилі у вакуумі (нм) */
    double theta_deg;   /* кут падіння (градуси) */
} tir_config_t;

/* Точка розрахованої таблиці зазору */
typedef struct {
    double gap_nm;
    double gap_relative;
    double transmission;
    double reflection;
} ftir_point_t;

static inline double deg_to_rad(double deg) {
    return deg * M_PI / 180.0;
}

/* Обчислення коефіцієнта загасання alpha (1/нм) та глибини проникнення dp (нм) */
int calculate_tir_params(const tir_config_t *cfg, double *alpha_out, double *dp_out) {
    if (!cfg || !alpha_out || !dp_out) return -1;
    
    double theta_rad = deg_to_rad(cfg->theta_deg);
    double sin_t = sin(theta_rad);
    double val = cfg->n1 * cfg->n1 * sin_t * sin_t - cfg->n2 * cfg->n2;
    
    if (val <= 0.0) {
        *alpha_out = 0.0;
        *dp_out = -1.0; /* кут менший за критичний */
        return 0;
    }
    
    double alpha = (2.0 * M_PI / cfg->lambda_nm) * sqrt(val);
    *alpha_out = alpha;
    *dp_out = 1.0 / alpha;
    return 1;
}

/* Обчислення коефіцієнта пропускання T(d) для s-поляризації */
double calculate_ftir_transmission(const tir_config_t *cfg, double gap_nm) {
    double alpha, dp;
    if (calculate_tir_params(cfg, &alpha, &dp) != 1 || dp < 0.0) {
        return 1.0; /* не режим ПВВ */
    }
    
    if (gap_nm <= 1e-9) {
        return 1.0; /* повний контакт */
    }
    
    double theta_rad = deg_to_rad(cfg->theta_deg);
    double sin_t = sin(theta_rad);
    double cos_t = cos(theta_rad);
    
    double val = cfg->n1 * cfg->n1 * sin_t * sin_t - cfg->n2 * cfg->n2;
    double num = (cfg->n1 * cfg->n1 - cfg->n2 * cfg->n2) * (cfg->n1 * cfg->n1 - cfg->n2 * cfg->n2);
    double den = 4.0 * cfg->n1 * cfg->n1 * val * cos_t * cos_t;
    double C = num / den;
    
    /* Захист від переповнення при великих зазорах alpha * gap > 700 */
    double arg = alpha * gap_nm;
    if (arg > 35.0) {
        /* Асимптотичне спрощення: sh(x) ≈ exp(x) / 2 */
        double exp_val = exp(-2.0 * arg);
        return (4.0 / C) * exp_val;
    }
    
    double sh_val = sinh(arg);
    double T = 1.0 / (1.0 + C * sh_val * sh_val);
    return T;
}

/* Розрахунок профілю згасання поля E(z) у зазорі */
void print_field_profile(const tir_config_t *cfg, double gap_nm, int num_steps) {
    double alpha, dp;
    if (calculate_tir_params(cfg, &alpha, &dp) != 1 || dp < 0.0) return;
    
    printf("\n--- Профіль електричного поля E(z) для зазору d = %.1f нм ---\n", gap_nm);
    printf("%-12s %-16s %-16s\n", "z (нм)", "z / d", "E(z) / E0");
    printf("---------------------------------------------\n");
    
    double ch_ad = cosh(alpha * gap_nm);
    for (int i = 0; i <= num_steps; ++i) {
        double z = i * (gap_nm / num_steps);
        double E_rel = cosh(alpha * (gap_nm - z)) / ch_ad;
        printf("%-12.1f %-16.3f %-16.6f\n", z, z / gap_nm, E_rel);
    }
}

int main(void) {
    tir_config_t cfg = {
        .n1 = 1.50,
        .n2 = 1.00,
        .n3 = 1.50,
        .lambda_nm = 632.8,
        .theta_deg = 45.0
    };

    double alpha, dp;
    int is_tir = calculate_tir_params(&cfg, &alpha, &dp);
    
    printf("=== Симуляція порушеного повного внутрішнього відбиття (FTIR) ===\n");
    printf("Параметри: n1=%.2f, n2=%.2f, n3=%.2f, lambda=%.1f нм, theta=%.1f deg\n",
           cfg.n1, cfg.n2, cfg.n3, cfg.lambda_nm, cfg.theta_deg);
    
    if (!is_tir || dp < 0.0) {
        printf("Помилка: кут падіння менший за критичний!\n");
        return EXIT_FAILURE;
    }
    
    printf("Глибина проникнення еванесцентного поля dp = %.2f нм\n\n", dp);
    printf("%-12s %-14s %-16s %-16s\n", "Зазор d (нм)", "d / lambda", "Пропускання T", "Відбиття R");
    printf("-------------------------------------------------------------\n");

    for (int step = 0; step <= 12; ++step) {
        double gap = step * (cfg.lambda_nm / 4.0);
        double T = calculate_ftir_transmission(&cfg, gap);
        double R = 1.0 - T;
        printf("%-12.1f %-14.3f %-16.6f %-16.6f\n", gap, gap / cfg.lambda_nm, T, R);
    }
    
    print_field_profile(&cfg, dp, 5);

    return EXIT_SUCCESS;
}
