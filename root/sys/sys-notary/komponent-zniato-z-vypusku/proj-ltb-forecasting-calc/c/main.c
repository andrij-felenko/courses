#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* ── Генератор випадкових чисел PCG32 ─────────────────────────────────────── */
typedef struct {
    uint64_t state;
    uint64_t inc;
} pcg32_random_t;

static inline uint32_t pcg32_random_r(pcg32_random_t *rng) {
    uint64_t oldstate = rng->state;
    rng->state = oldstate * 6364136223846793005ULL + (rng->inc | 1);
    uint32_t xorshifted = (uint32_t)(((oldstate >> 18u) ^ oldstate) >> 27u);
    uint32_t rot = (uint32_t)(oldstate >> 59u);
    return (xorshifted >> rot) | (xorshifted << ((-rot) & 31));
}

static inline double pcg32_uniform_double(pcg32_random_t *rng) {
    return (double)pcg32_random_r(rng) / 4294967296.0;
}

/* Генерація стандартного нормального розподілу N(0, 1) за методом Бокса-Мюллера */
static double pcg32_gaussian(pcg32_random_t *rng, double mu, double sigma) {
    double u1 = pcg32_uniform_double(rng);
    double u2 = pcg32_uniform_double(rng);
    while (u1 <= 1e-15) u1 = pcg32_uniform_double(rng);
    
    double z0 = sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
    return mu + z0 * sigma;
}

/* Генерація випадкової величини за розподілом Вейбулла W(beta, eta) */
static double pcg32_weibull(pcg32_random_t *rng, double beta, double eta) {
    double u = pcg32_uniform_double(rng);
    while (u <= 1e-15 || u >= 1.0) u = pcg32_uniform_double(rng);
    return eta * pow(-log(1.0 - u), 1.0 / beta);
}

/* ── Структури параметрів та результатів моделювання ─────────────────────── */
typedef struct {
    uint32_t horizon_quarters;      /* Залишковий горизонт випуску, кварталів */
    double   quarterly_demand_mean; /* Середній квартальний випуск виробів */
    double   quarterly_demand_std;  /* Волатильність попиту (sigma) */
    double   smt_scrap_rate;        /* Коефіцієнт технологічного браку (наприклад 0.015) */
    uint32_t feeder_setup_loss;     /* Втрати на заправку живильника на квартал */
    
    /* Параметри сервісного обслуговування */
    uint32_t active_installed_base; /* Парк виробів в експлуатації */
    double   weibull_beta;          /* Параметр форми Вейбулла (1.0 = експонента, >1 = старіння) */
    double   weibull_eta_quarters;  /* Характеристичний ресурс чіпа в кварталах */
    uint32_t warranty_years;        /* Строк гарантійних зобов'язань */
    
    /* Економічні параметри */
    double   unit_cost_usd;         /* Закупівельна ціна чіпа за LTB */
    double   holding_cost_rate_yr;  /* Річна ставка утримання запасів (0.18 = 18%) */
    double   shortage_penalty_usd;  /* Штраф за одиницю дефіциту */
    double   salvage_value_usd;     /* Ліквідаційна вартість невикористаного чіпа */
    
    uint32_t mc_iterations;         /* Кількість ітерацій Монте-Карло */
} ltb_config_t;

typedef struct {
    double   mean_required_units;
    double   std_dev_units;
    double   min_units;
    double   max_units;
    double   percentile_50;         /* Медіана */
    double   percentile_80;         /* 80% рівень надійності */
    double   percentile_95;         /* 95% рівень надійності */
    double   percentile_99;         /* 99% рівень надійності */
    
    /* Оптимальний обсяг закупівлі за мінімумом TCO */
    uint32_t optimal_order_quantity;
    double   expected_min_cost_usd;
    double   holding_cost_usd;
    double   expected_shortage_cost_usd;
    double   expected_scrap_cost_usd;
} ltb_simulation_result_t;

/* Функція порівняння для qsort */
static int compare_doubles(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    return (da > db) - (da < db);
}

/* ── Головне ядро симуляції Монте-Карло ───────────────────────────────────── */
int ltb_run_simulation(const ltb_config_t *cfg, ltb_simulation_result_t *res) {
    if (!cfg || !res || cfg->mc_iterations < 100 || cfg->horizon_quarters == 0) {
        return -1;
    }

    double *simulated_demands = (double *)malloc(cfg->mc_iterations * sizeof(double));
    if (!simulated_demands) return -2;

    pcg32_random_t rng = { .state = 0x853c49e6748fea9bULL, .inc = 0xda3e39cb94b95bdbULL };

    double sum_demands = 0.0;
    double sum_demands_sq = 0.0;
    double min_dem = 1e12;
    double max_dem = 0.0;

    double q_holding_cost_rate = cfg->holding_cost_rate_yr / 4.0;

    for (uint32_t iter = 0; iter < cfg->mc_iterations; ++iter) {
        double total_demand_iter = 0.0;

        /* 1. Моделювання виробничого попиту по кварталах */
        for (uint32_t q = 0; q < cfg->horizon_quarters; ++q) {
            double q_prod = pcg32_gaussian(&rng, cfg->quarterly_demand_mean, cfg->quarterly_demand_std);
            if (q_prod < 0.0) q_prod = 0.0;

            /* Додавання технологічного браку монтажу та наладки */
            double q_scrap = (q_prod * cfg->smt_scrap_rate) + (double)cfg->feeder_setup_loss;
            total_demand_iter += (q_prod + q_scrap);
        }

        /* 2. Моделювання сервісних відмов парку за розподілом Вейбулла */
        uint32_t total_service_quarters = cfg->warranty_years * 4;
        double current_active_base = (double)cfg->active_installed_base;

        for (uint32_t sq = 0; sq < total_service_quarters; ++sq) {
            double t_start = (double)sq;
            double t_end = (double)(sq + 1);

            double f_start = 1.0 - exp(-pow(t_start / cfg->weibull_eta_quarters, cfg->weibull_beta));
            double f_end   = 1.0 - exp(-pow(t_end   / cfg->weibull_eta_quarters, cfg->weibull_beta));

            double fail_prob = 0.0;
            if (f_start < 0.9999) {
                fail_prob = (f_end - f_start) / (1.0 - f_start);
            }

            double failures = current_active_base * fail_prob;
            total_demand_iter += failures;
        }

        simulated_demands[iter] = total_demand_iter;
        sum_demands += total_demand_iter;
        sum_demands_sq += (total_demand_iter * total_demand_iter);

        if (total_demand_iter < min_dem) min_dem = total_demand_iter;
        if (total_demand_iter > max_dem) max_dem = total_demand_iter;
    }

    /* Статистичний аналіз вибірки */
    double mean = sum_demands / cfg->mc_iterations;
    double variance = (sum_demands_sq / cfg->mc_iterations) - (mean * mean);
    if (variance < 0.0) variance = 0.0;
    double std_dev = sqrt(variance);

    qsort(simulated_demands, cfg->mc_iterations, sizeof(double), compare_doubles);

    res->mean_required_units = mean;
    res->std_dev_units = std_dev;
    res->min_units = min_dem;
    res->max_units = max_dem;
    res->percentile_50 = simulated_demands[(uint32_t)(cfg->mc_iterations * 0.50)];
    res->percentile_80 = simulated_demands[(uint32_t)(cfg->mc_iterations * 0.80)];
    res->percentile_95 = simulated_demands[(uint32_t)(cfg->mc_iterations * 0.95)];
    res->percentile_99 = simulated_demands[(uint32_t)(cfg->mc_iterations * 0.99)];

    /* 3. Оптимізація обсягу закупівлі за критерієм мінімуму TCO */
    uint32_t min_order = (uint32_t)(res->percentile_50 * 0.7);
    uint32_t max_order = (uint32_t)(res->percentile_99 * 1.3);
    uint32_t step = (max_order - min_order) / 100;
    if (step == 0) step = 1;

    double lowest_total_cost = 1e18;
    uint32_t best_order_qty = (uint32_t)res->percentile_95;
    double best_holding = 0.0, best_shortage = 0.0, best_scrap = 0.0;

    for (uint32_t q_candidate = min_order; q_candidate <= max_order; q_candidate += step) {
        double iter_holding_cost = 0.0;
        double iter_shortage_cost = 0.0;
        double iter_scrap_cost = 0.0;

        for (uint32_t i = 0; i < cfg->mc_iterations; ++i) {
            double actual_dem = simulated_demands[i];
            if (q_candidate > actual_dem) {
                /* Надлишок: вартість списання та утримання залишку */
                double surplus = (double)q_candidate - actual_dem;
                iter_scrap_cost += surplus * (cfg->unit_cost_usd - cfg->salvage_value_usd);
                iter_holding_cost += ((double)q_candidate + actual_dem) * 0.5 * 
                                     q_holding_cost_rate * cfg->horizon_quarters * cfg->unit_cost_usd;
            } else {
                /* Дефіцит: штраф за недопоставку */
                double shortage = actual_dem - (double)q_candidate;
                iter_shortage_cost += shortage * cfg->shortage_penalty_usd;
                iter_holding_cost += (double)q_candidate * 0.5 * 
                                     q_holding_cost_rate * (cfg->horizon_quarters / 2.0) * cfg->unit_cost_usd;
            }
        }

        iter_holding_cost /= cfg->mc_iterations;
        iter_shortage_cost /= cfg->mc_iterations;
        iter_scrap_cost /= cfg->mc_iterations;

        double purchase_cost = (double)q_candidate * cfg->unit_cost_usd;
        double total_tco = purchase_cost + iter_holding_cost + iter_shortage_cost + iter_scrap_cost;

        if (total_tco < lowest_total_cost) {
            lowest_total_cost = total_tco;
            best_order_qty = q_candidate;
            best_holding = iter_holding_cost;
            best_shortage = iter_shortage_cost;
            best_scrap = iter_scrap_cost;
        }
    }

    res->optimal_order_quantity = best_order_qty;
    res->expected_min_cost_usd = lowest_total_cost;
    res->holding_cost_usd = best_holding;
    res->expected_shortage_cost_usd = best_shortage;
    res->expected_scrap_cost_usd = best_scrap;

    free(simulated_demands);
    return 0;
}

/* ── Консольна демонстраційна програма ────────────────────────────────────── */
int main(void) {
    ltb_config_t config = {
        .horizon_quarters      = 12,      /* 3 роки залишкового випуску */
        .quarterly_demand_mean = 2500.0,  /* 10 000 виробів на рік */
        .quarterly_demand_std  = 350.0,   /* 14% дисперсія попиту */
        .smt_scrap_rate        = 0.015,   /* 1.5% технологічного браку */
        .feeder_setup_loss     = 30,      /* 30 чіпів на квартальну переналадку */
        
        .active_installed_base = 40000,   /* 40 000 пристроїв в експлуатації */
        .weibull_beta          = 1.4,     /* Старіння кристалів (поступовий знос) */
        .weibull_eta_quarters  = 80.0,    /* Характеристичний ресурс 20 років */
        .warranty_years        = 5,       /* 5 років гарантії */
        
        .unit_cost_usd         = 12.50,   /* Ціна одного чіпа */
        .holding_cost_rate_yr  = 0.18,    /* 18% річних на утримання запасів */
        .shortage_penalty_usd  = 120.00,  /* 120 USD штрафу за дефіцитний прилад */
        .salvage_value_usd     = 1.00,    /* 1 USD залишкової вартості при списанні */
        
        .mc_iterations         = 10000    /* 10 000 ітерацій Монте-Карло */
    };

    ltb_simulation_result_t result;
    printf("Запуск імітаційного моделювання LTB (Монте-Карло, %u ітерацій)...\n", config.mc_iterations);

    int status = ltb_run_simulation(&config, &result);
    if (status != 0) {
        fprintf(stderr, "Помилка симуляції: код %d\n", status);
        return 1;
    }

    printf("\n===============================================================\n");
    printf("   РЕЗУЛЬТАТИ ПРОГНОЗУВАННЯ ПОТРЕБИ ОСТАННЬОЇ ЗАКУПІВЛІ (LTB)  \n");
    printf("===============================================================\n");
    printf("Середня очікувана потреба:    %8.0f шт. (сигма: ±%.0f шт.)\n", 
           result.mean_required_units, result.std_dev_units);
    printf("Діапазон розкиду (Min .. Max): %8.0f .. %.0f шт.\n", 
           result.min_units, result.max_units);
    printf("---------------------------------------------------------------\n");
    printf("КВАНТИЛЬНИЙ АНАЛІЗ РИЗИКІВ ДЕФІЦИТУ:\n");
    printf("  • 50%% рівень (Медіана):     %8.0f шт.\n", result.percentile_50);
    printf("  • 80%% рівень надійності:   %8.0f шт.\n", result.percentile_80);
    printf("  • 95%% рівень надійності:   %8.0f шт.\n", result.percentile_95);
    printf("  • 99%% рівень надійності:   %8.0f шт.\n", result.percentile_99);
    printf("---------------------------------------------------------------\n");
    printf("ЕКОНОМІЧНА ОПТИМІЗАЦІЯ СУКУПНОЇ ВАРТОСТІ ВОЛОДІННЯ (TCO):\n");
    printf("  ★ РЕКОМЕНДОВАНИЙ ОБСЯГ LTB:   %8u шт.\n", result.optimal_order_quantity);
    printf("  • Прямі витрати на закупівлю: %8.2f USD\n", (double)result.optimal_order_quantity * config.unit_cost_usd);
    printf("  • Очікувана вартість зберігання: %6.2f USD\n", result.holding_cost_usd);
    printf("  • Очікуваний ризик дефіциту:    %6.2f USD\n", result.expected_shortage_cost_usd);
    printf("  • Очікуваний ризик списання:    %6.2f USD\n", result.expected_scrap_cost_usd);
    printf("  • МІНІМАЛЬНІ СУМАРНІ ВИТРАТИ:   %8.2f USD\n", result.expected_min_cost_usd);
    printf("===============================================================\n");

    return 0;
}
