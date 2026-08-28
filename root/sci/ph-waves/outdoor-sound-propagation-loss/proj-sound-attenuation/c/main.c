#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Структура вхідних параметрів навколишнього середовища */
typedef struct {
    double temperature_c;       /* Температура повітря, °C */
    double pressure_kpa;        /* Атмосферний тиск, кПа */
    double relative_humidity;   /* Відносна вологість, % (0..100) */
} iso9613_env_t;

/* Структура результатів розрахунку */
typedef struct {
    double alpha_db_m;          /* Коефіцієнт загасання, дБ/м */
    double alpha_db_km;         /* Коефіцієнт загасання, дБ/км */
    double fr_oxygen_hz;        /* Частота релаксації кисню, Гц */
    double fr_nitrogen_hz;      /* Частота релаксації азоту, Гц */
    double molar_humidity_pct;  /* Концентрація водяної пари, % */
} iso9613_result_t;

/* Обчислення поглинання за стандартом ISO 9613-1 */
bool iso9613_calculate(const iso9613_env_t *env, double frequency_hz, iso9613_result_t *out) {
    if (!env || !out || frequency_hz <= 0.0) {
        return false;
    }
    if (env->relative_humidity < 0.0 || env->relative_humidity > 100.0) {
        return false;
    }

    const double p_pr = 101.325; /* Стандартний тиск, кПа */
    const double T_pr = 293.15;  /* Стандартна температура, К */
    const double T_01 = 273.16;  /* Потрійна точка води, К */

    double T_k = env->temperature_c + 273.15;
    if (T_k <= 0.0) return false;

    double p_rel = env->pressure_kpa / p_pr;
    double T_rel = T_k / T_pr;

    /* 1. Молярна концентрація водяної пари h */
    double exp_val = -6.8346 * math.pow(T_01 / T_k, 1.261) + 4.6151;
    double p_sat_rel = math.pow(10.0, exp_val);
    double h = env->relative_humidity * (p_sat_rel / p_rel);

    /* 2. Частоти релаксації кисню та азоту */
    double fr_O = p_rel * (24.0 + 4.04e4 * h * (0.02 + h) / (0.391 + h));
    double fr_N = p_rel * math.pow(T_rel, -0.5) * 
                   (9.0 + 280.0 * h * math.exp(-4.17 * (math.pow(T_rel, -1.0/3.0) - 1.0)));

    /* 3. Три складові коефіцієнта поглинання */
    double alpha_cl_term = 1.84e-11 * (1.0 / p_rel) * math.sqrt(T_rel);
    double alpha_O_term  = math.pow(T_rel, -2.5) * 0.1068 * math.exp(-3352.0 / T_k) * 
                           (fr_O / (fr_O * fr_O + frequency_hz * frequency_hz));
    double alpha_N_term  = math.pow(T_rel, -2.5) * 0.01275 * math.exp(-2239.1 / T_k) * 
                           (fr_N / (fr_N * fr_N + frequency_hz * frequency_hz));

    double f2 = frequency_hz * frequency_hz;
    double alpha_db_m = 8.686 * f2 * (alpha_cl_term + alpha_O_term + alpha_N_term);

    out->alpha_db_m = alpha_db_m;
    out->alpha_db_km = alpha_db_m * 1000.0;
    out->fr_oxygen_hz = fr_O;
    out->fr_nitrogen_hz = fr_N;
    out->molar_humidity_pct = h;

    return true;
}

/* Розрахунок підсумкового рівня звукового тиску (SPL) на відстані r */
double calculate_spl_at_distance(double spl_initial, double r_initial_m, 
                                double r_target_m, double alpha_db_m) {
    if (r_target_m <= r_initial_m || r_initial_m <= 0.0) {
        return spl_initial;
    }
    double div_loss = 20.0 * log10(r_target_m / r_initial_m);
    double abs_loss = alpha_db_m * (r_target_m - r_initial_m);
    return spl_initial - div_loss - abs_loss;
}

int main(void) {
    iso9613_env_t env = {
        .temperature_c = 20.0,
        .pressure_kpa = 101.325,
        .relative_humidity = 50.0
    };

    double freq = 4000.0; /* 4 кГц */
    iso9613_result_t res;

    if (iso9613_calculate(&env, freq, &res)) {
        printf("=== ISO 9613-1 Розрахунок (C) ===\n");
        printf("Частота: %.1f Гц | T: %.1f C | RH: %.1f %%\n", freq, env.temperature_c, env.relative_humidity);
        printf("Частота релаксації O2: %.1f Гц\n", res.fr_oxygen_hz);
        printf("Частота релаксації N2: %.1f Гц\n", res.fr_nitrogen_hz);
        printf("Коефіцієнт поглинання alpha: %.5f дБ/м (%.2f дБ/км)\n", res.alpha_db_m, res.alpha_db_km);

        double spl_10m = 100.0;
        double r_target = 1000.0;
        double spl_1km = calculate_spl_at_distance(spl_10m, 10.0, r_target, res.alpha_db_m);
        printf("SPL на 10 м: %.1f дБ -> SPL на 1000 м: %.1f дБ\n", spl_10m, spl_1km);
    }
    return 0;
}
