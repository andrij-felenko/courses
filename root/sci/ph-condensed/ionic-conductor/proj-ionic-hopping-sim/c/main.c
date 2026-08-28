#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

/* Фізичні константи */
#define KB_EV 8.61733326e-5    /* Константа Больцмана в еВ/К */
#define KB_JOULES 1.380649e-23  /* Константа Больцмана в Дж/К */
#define CHARGE_COULOMBS 1.60217663e-19 /* Елементарний заряд в Кл */
#define ELEMENTARY_CHARGE 1.0  /* Заряд іона в одиницях e */

typedef struct {
    double temp_k;            /* Температура в Кельвінах */
    double barrier_ev;        /* Енергія активації E_a в еВ */
    double electric_field;    /* Напруженість поля E в В/м */
    double lattice_a_m;       /* Період ґратки a в метрах */
    double nu_0_hz;           /* Частота спроб ν₀ в Гц */
    size_t num_ions;          /* Кількість іонів у симуляції */
    size_t num_steps;         /* Кількість часових кроків */
    double dt_sec;            /* Тривалість одного кроку в секундах */
} SimConfig;

typedef struct {
    double mean_displacement_m; /* Середній зсув <x> в метрах */
    double mean_sq_displacement;/* Середній квадрат зсуву <x²> */
    double drift_velocity_m_s;  /* Дрейфова швидкість v_drift в м/с */
    double diffusion_coeff_m2_s;/* Коефіцієнт дифузії D в м²/с */
    double nernst_einstein_sim; /* Симульоване співвідношення μ/D */
    double nernst_einstein_theor;/* Теоретичне співвідношення q/(k_B*T) */
} SimResults;

/* Генератор випадкового числа в діапазоні [0, 1) */
static double get_random_uniform(void) {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

SimResults run_hopping_simulation(const SimConfig *cfg) {
    SimResults res = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    
    /* Енергетичне зміщення бар'єра під дією поля: ΔU = q * a * E / 2 в еВ */
    double delta_u_ev = (ELEMENTARY_CHARGE * cfg->lattice_a_m * cfg->electric_field) / 2.0;
    
    /* Частоти стрибків по полю та проти поля */
    double barrier_fwd = cfg->barrier_ev - delta_u_ev;
    double barrier_bwd = cfg->barrier_ev + delta_u_ev;
    
    double nu_fwd = cfg->nu_0_hz * exp(-barrier_fwd / (KB_EV * cfg->temp_k));
    double nu_bwd = cfg->nu_0_hz * exp(-barrier_bwd / (KB_EV * cfg->temp_k));
    
    double p_fwd = nu_fwd * cfg->dt_sec;
    double p_bwd = nu_bwd * cfg->dt_sec;
    
    if (p_fwd + p_bwd >= 1.0) {
        fprintf(stderr, "Помилка: Δt занадто великий! p_total = %f >= 1.0\n", p_fwd + p_bwd);
        return res;
    }
    
    /* Виділення пам'яті для координат іонів */
    double *positions = (double *)calloc(cfg->num_ions, sizeof(double));
    if (!positions) {
        fprintf(stderr, "Помилка виділення пам'яті.\n");
        return res;
    }
    
    /* Головний цикл симуляції */
    for (size_t step = 0; step < cfg->num_steps; ++step) {
        for (size_t i = 0; i < cfg->num_ions; ++i) {
            double r = get_random_uniform();
            if (r < p_fwd) {
                positions[i] += cfg->lattice_a_m;
            } else if (r < p_fwd + p_bwd) {
                positions[i] -= cfg->lattice_a_m;
            }
        }
    }
    
    /* Статистична обробка результатів */
    double sum_x = 0.0;
    double sum_x2 = 0.0;
    for (size_t i = 0; i < cfg->num_ions; ++i) {
        sum_x += positions[i];
        sum_x2 += positions[i] * positions[i];
    }
    
    double total_time = cfg->num_steps * cfg->dt_sec;
    res.mean_displacement_m = sum_x / (double)cfg->num_ions;
    res.mean_sq_displacement = sum_x2 / (double)cfg->num_ions;
    res.drift_velocity_m_s = res.mean_displacement_m / total_time;
    
    /* Коефіцієнт дифузії за дисперсією: D = (<x²> - <x>²) / (2 * t) */
    double variance = res.mean_sq_displacement - (res.mean_displacement_m * res.mean_displacement_m);
    res.diffusion_coeff_m2_s = variance / (2.0 * total_time);
    
    /* Розрахунок рухливості μ = v_drift / E */
    double mobility = res.drift_velocity_m_s / cfg->electric_field;
    res.nernst_einstein_sim = mobility / res.diffusion_coeff_m2_s;
    res.nernst_einstein_theor = CHARGE_COULOMBS / (KB_JOULES * cfg->temp_k);
    
    free(positions);
    return res;
}

int main(void) {
    srand((unsigned int)time(NULL));
    
    SimConfig cfg = {
        .temp_k = 500.0,            /* 500 K */
        .barrier_ev = 0.4,          /* Бар'єр 0.4 еВ */
        .electric_field = 1.0e5,    /* Поле 10⁵ В/м */
        .lattice_a_m = 3.0e-10,     /* Крок ґратки 3 Å */
        .nu_0_hz = 1.0e12,          /* 1 ТГц */
        .num_ions = 10000,          /* 10 000 іонів */
        .num_steps = 1000,          /* 1000 кроків */
        .dt_sec = 1.0e-9            /* 1 нс */
    };
    
    printf("=== Симуляція іонних стрибків (C99) ===\n");
    printf("Температура: %.1f K, Поле: %.1e В/м\n", cfg.temp_k, cfg.electric_field);
    
    SimResults res = run_hopping_simulation(&cfg);
    
    printf("Середній зсув <x>:          %.3e м\n", res.mean_displacement_m);
    printf("Дрейфова швидкість v_drift:  %.3e м/с\n", res.drift_velocity_m_s);
    printf("Коефіцієнт дифузії D:        %.3e м²/с\n", res.diffusion_coeff_m2_s);
    printf("Симульоване μ/D:             %.3e В⁻¹\n", res.nernst_einstein_sim);
    printf("Теоретичне q/(k_B*T):        %.3e В⁻¹\n", res.nernst_einstein_theor);
    
    return 0;
}
