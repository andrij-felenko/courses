#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Фізичні константи та параметри гетероструктури YIG/Pt */
#define ELECTRON_CHARGE 1.602176634e-19   /* Кл */
#define REDUCED_PLANCK 1.054571817e-34    /* Дж·с */
#define BOLTZMANN_CONST 1.380649e-23      /* Дж/К */

typedef struct {
    int num_points;         /* Кількість вузлів сітки */
    double layer_thickness;  /* Товщина YIG шару (м) */
    double lambda_m;         /* Довжина дифузії магнонів (м) */
    double sigma_m;          /* Магнонна спінова провідність (Ом^-1·м^-1) */
    double g_mix;            /* Спінова провідність змішування (м^-2) */
    double theta_sh;         /* Спіновий кут Холла для Pt */
    double rho_pt;           /* Питомий опір Pt (Ом·м) */
    double pt_thickness;     /* Товщина шару Pt (м) */
    double sample_width;     /* Ширина зразка (м) */
    double temp_cold;        /* Температура на холодному краї (К) */
    double temp_hot;         /* Температура на гарячому краї (К) */
} SimConfig;

typedef struct {
    double* z_mesh;          /* Просторова сітка (м) */
    double* mu_m;            /* Магнонний хімічний потенціал (Дж) */
    double* temp_profile;    /* Профіль температури (К) */
    int points;
    double ishe_voltage;     /* Розрахована напруга ISHE (В) */
    double spin_current;     /* Інжектований спіновий струм (Дж/м^2) */
} SimResult;

/* Ініціалізація конфігурації за замовчуванням */
static SimConfig create_default_config(void) {
    SimConfig cfg;
    cfg.num_points = 500;
    cfg.layer_thickness = 1.0e-6;   /* 1 мікрометр YIG */
    cfg.lambda_m = 100.0e-9;         /* 100 нанометрів */
    cfg.sigma_m = 1.0e3;             /* 1000 Ом^-1·м^-1 */
    cfg.g_mix = 1.0e18;              /* 1e18 м^-2 */
    cfg.theta_sh = 0.08;             /* 8% для Pt */
    cfg.rho_pt = 2.0e-7;             /* 200 нОм·м */
    cfg.pt_thickness = 10.0e-9;      /* 10 нм Pt */
    cfg.sample_width = 5.0e-3;       /* 5 мм */
    cfg.temp_cold = 300.0;           /* 300 К */
    cfg.temp_hot = 310.0;            /* 310 К (ΔT = 10 K) */
    return cfg;
}

/* Виділення пам'яті для результатів */
static SimResult* allocate_result(int points) {
    SimResult* res = (SimResult*)malloc(sizeof(SimResult));
    if (!res) return NULL;
    res->points = points;
    res->z_mesh = (double*)malloc((size_t)points * sizeof(double));
    res->mu_m = (double*)malloc((size_t)points * sizeof(double));
    res->temp_profile = (double*)malloc((size_t)points * sizeof(double));
    if (!res->z_mesh || !res->mu_m || !res->temp_profile) {
        free(res->z_mesh);
        free(res->mu_m);
        free(res->temp_profile);
        free(res);
        return NULL;
    }
    return res;
}

/* Звільнення пам'яті */
static void free_result(SimResult* res) {
    if (!res) return;
    free(res->z_mesh);
    free(res->mu_m);
    free(res->temp_profile);
    free(res);
}

/* Чисельний розрахунок профілю методом релаксації */
static bool run_simulation(const SimConfig* cfg, SimResult* res) {
    const int N = cfg->num_points;
    const double dz = cfg->layer_thickness / (double)(N - 1);
    const double dz_sq = dz * dz;
    const double inv_lambda_sq = 1.0 / (cfg->lambda_m * cfg->lambda_m);
    const double denom = 2.0 + dz_sq * inv_lambda_sq;

    /* Створення сітки та температури */
    for (int i = 0; i < N; ++i) {
        res->z_mesh[i] = (double)i * dz;
        res->temp_profile[i] = cfg->temp_cold + 
            (cfg->temp_hot - cfg->temp_cold) * (res->z_mesh[i] / cfg->layer_thickness);
        res->mu_m[i] = 0.0; /* Початкове наближення */
    }

    /* Тимчасовий буфер для ітерацій */
    double* next_mu = (double*)malloc((size_t)N * sizeof(double));
    if (!next_mu) return false;

    const int max_iterations = 100000;
    const double tolerance = 1.0e-12;

    for (int iter = 0; iter < max_iterations; ++iter) {
        double max_change = 0.0;

        /* Внутрішні вузли сітки */
        for (int i = 1; i < N - 1; ++i) {
            next_mu[i] = (res->mu_m[i - 1] + res->mu_m[i + 1]) / denom;
            double diff = fabs(next_mu[i] - res->mu_m[i]);
            if (diff > max_change) max_change = diff;
        }

        /* Гранична умова Neumann при z = 0 (ізольована межа) */
        next_mu[0] = next_mu[1];

        /* Гранична умова при z = L (інжекція у важкий метал) */
        const double alpha = (cfg->g_mix * ELECTRON_CHARGE) / (M_PI * cfg->sigma_m);
        next_mu[N - 1] = next_mu[N - 2] / (1.0 + dz * alpha);

        /* Оновлення масиву */
        for (int i = 0; i < N; ++i) {
            res->mu_m[i] = next_mu[i];
        }

        if (max_change < tolerance && iter > 100) break;
    }

    free(next_mu);

    /* Розрахунок підсумкових фізичних величин */
    double boundary_mu = res->mu_m[N - 1];
    res->spin_current = (cfg->g_mix / (2.0 * M_PI)) * boundary_mu;
    
    /* V_ISHE = θ_SH * (ρ_Pt / d_Pt) * w * J_s */
    res->ishe_voltage = cfg->theta_sh * (cfg->rho_pt / cfg->pt_thickness) * 
                        cfg->sample_width * res->spin_current * (ELECTRON_CHARGE / REDUCED_PLANCK);

    return true;
}

int main(void) {
    SimConfig cfg = create_default_config();
    SimResult* res = allocate_result(cfg.num_points);
    if (!res) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    if (run_simulation(&cfg, res)) {
        printf("=== Результати розрахунку магнонної дифузії YIG/Pt ===\n");
        printf("Товщина YIG: %.2f мкм\n", cfg.layer_thickness * 1.0e6);
        printf("Різниця температур ΔT: %.1f K\n", cfg.temp_hot - cfg.temp_cold);
        printf("Магнонне накопичення на межі z=L: %.4e Дж\n", res->mu_m[res->points - 1]);
        printf("Інжектований спіновий струм J_s: %.4e Дж/м^2\n", res->spin_current);
        printf("Розрахована напруга ISHE: %.4e В (%.2f мкВ)\n", 
               res->ishe_voltage, res->ishe_voltage * 1.0e6);
    }

    free_result(res);
    return 0;
}
