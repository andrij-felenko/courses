/* spc_engine.h / spc_engine.c - C99 */
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    const char* param_name;
    double golden_nominal;
    double lsl;
    double usl;
} spc_spec_t;

typedef struct {
    size_t count;
    double mean;
    double m2;      /* Накопичена сума квадратів відхилень за Велфордом */
    double min_val;
    double max_val;
} spc_accumulator_t;

typedef struct {
    double mean;
    double std_dev;
    double cp;
    double cpu;
    double cpl;
    double cpk;
    double mean_drift_from_golden;
    bool is_capable;          /* Cpk >= 1.33 */
    bool is_high_quality;     /* Cpk >= 1.67 */
} spc_result_t;

void spc_acc_init(spc_accumulator_t* acc) {
    acc->count = 0;
    acc->mean = 0.0;
    acc->m2 = 0.0;
    acc->min_val = 1e30;
    acc->max_val = -1e30;
}

/* Онлайн-додавання виміру за алгоритмом Велфорда */
void spc_acc_update(spc_accumulator_t* acc, double x) {
    acc->count++;
    double delta = x - acc->mean;
    acc->mean += delta / (double)acc->count;
    double delta2 = x - acc->mean;
    acc->m2 += delta * delta2;

    if (x < acc->min_val) acc->min_val = x;
    if (x > acc->max_val) acc->max_val = x;
}

bool spc_evaluate(const spc_accumulator_t* acc, const spc_spec_t* spec, spc_result_t* res) {
    if (acc->count < 3 || spec->usl <= spec->lsl) {
        return false;
    }

    double variance = acc->m2 / (double)(acc->count - 1);
    double std_dev = sqrt(variance);
    if (std_dev < 1e-12) {
        /* Нульова дисперсія - вироджений випадок */
        std_dev = 1e-12;
    }

    double spec_width = spec->usl - spec->lsl;
    double cp = spec_width / (6.0 * std_dev);
    double cpu = (spec->usl - acc->mean) / (3.0 * std_dev);
    double cpl = (acc->mean - spec->lsl) / (3.0 * std_dev);
    double cpk = (cpu < cpl) ? cpu : cpl;

    res->mean = acc->mean;
    res->std_dev = std_dev;
    res->cp = cp;
    res->cpu = cpu;
    res->cpl = cpl;
    res->cpk = cpk;
    res->mean_drift_from_golden = acc->mean - spec->golden_nominal;
    res->is_capable = (cpk >= 1.33);
    res->is_high_quality = (cpk >= 1.67);

    return true;
}

void spc_print_report(const spc_spec_t* spec, const spc_result_t* res, size_t sample_size) {
    printf("=== SPC АНАЛІЗ ПАРАМЕТРА: %s (Вибірка N = %zu) ===\n", spec->param_name, sample_size);
    printf("  Номінал Golden Sample: %8.4f\n", spec->golden_nominal);
    printf("  Межі специфікації     : [%8.4f ... %8.4f]\n", spec->lsl, spec->usl);
    printf("  Фактичне середнє (μ)  : %8.4f (Дрейф від еталона: %+8.4f)\n", 
           res->mean, res->mean_drift_from_golden);
    printf("  Стандартне відхил. (σ): %8.4f\n", res->std_dev);
    printf("  Індекс придатності Cp : %8.4f\n", res->cp);
    printf("  Індекс придатності Cpk: %8.4f (Cpu: %.3f, Cpl: %.3f)\n", 
           res->cpk, res->cpu, res->cpl);
    printf("  Вердикт придатності   : %s\n\n", 
           res->is_high_quality ? "ВІДПОВІДАЄ СЕРІЇ 5-SIGMA (Висока надійність)" :
           res->is_capable      ? "ПРИДАТНО ДЛЯ МАСОВОГО ВИРОБНИЦТВА (Cpk >= 1.33)" :
                                  "НЕПРИДАТНО / КРИТИЧНИЙ ДРЕЙФ (Потрібне 100% сортування)");
}
