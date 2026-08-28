#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

#if defined(_MSC_VER)
#include <intrin.h>
#else
#include <x86intrin.h>
#endif

/* Однопрохідний чисельно стабільний акумулятор статистики Велфорда */
typedef struct {
    double mean;
    double m2;
    uint64_t count;
} OnlineStats;

void stats_update(OnlineStats *s, double val) {
    s->count++;
    double delta = val - s->mean;
    s->mean += delta / (double)s->count;
    double delta2 = val - s->mean;
    s->m2 += delta * delta2;
}

double stats_variance(const OnlineStats *s) {
    return s->count > 1 ? s->m2 / (double)(s->count - 1) : 0.0;
}

/* Обчислення статистики t-критерію Велча для двох незалежних вибірок */
double welch_t_statistic(const OnlineStats *a, const OnlineStats *b) {
    double var_a = stats_variance(a);
    double var_b = stats_variance(b);
    double num = a->mean - b->mean;
    double den = sqrt((var_a / (double)a->count) + (var_b / (double)b->count));
    return den > 0.0 ? num / den : 0.0;
}

/* Зчитування апаратного лічильника тактів із серіалізацією процесорного конвеєра */
static inline uint64_t read_tsc_serialized(void) {
    #if defined(_MSC_VER)
    return __rdtsc();
    #else
    unsigned int aux;
    return __rdtscp(&aux);
    #endif
}

/* Демонстраційний запуск верифікації функції ct_memcmp */
void run_dudect_verification(size_t num_measurements) {
    OnlineStats fixed_stats = {0};
    OnlineStats random_stats = {0};

    uint8_t key_fixed[32];
    uint8_t input_fixed[32];
    uint8_t input_random[32];

    for (int i = 0; i < 32; ++i) {
        key_fixed[i] = 0x5A;
        input_fixed[i] = 0x5A;
    }

    for (size_t i = 0; i < num_measurements; ++i) {
        /* Клас A: Ідентичні буфери */
        uint64_t t0 = read_tsc_serialized();
        volatile int r1 = ct_memcmp(key_fixed, input_fixed, 32);
        uint64_t t1 = read_tsc_serialized();
        (void)r1;
        stats_update(&fixed_stats, (double)(t1 - t0));

        /* Клас B: Випадковий неспівпалий буфер */
        for (int j = 0; j < 32; ++j) {
            input_random[j] = (uint8_t)rand();
        }
        uint64_t t2 = read_tsc_serialized();
        volatile int r2 = ct_memcmp(key_fixed, input_random, 32);
        uint64_t t3 = read_tsc_serialized();
        (void)r2;
        stats_update(&random_stats, (double)(t3 - t2));
    }

    double t_stat = welch_t_statistic(&fixed_stats, &random_stats);
    printf("TVLA Dudect Результат: t-значення = %.3f (вибірка %zu)\n", t_stat, num_measurements);
    if (fabs(t_stat) > 4.5) {
        printf("УВАГА: Виявлено статистичний витік часу (|t| > 4.5)!\n");
    } else {
        printf("УСПІХ: Код є стійким до часових побічних каналів (|t| <= 4.5).\n");
    }
}
