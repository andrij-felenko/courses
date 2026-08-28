#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define MAX_NODES 16
#define NUM_TRIALS 50000

/* Архітектурні параметри конфігурації кластера */
typedef struct {
    int total_nodes;       /* Загальна кількість вузлів N */
    int write_quorum;      /* Розмір кворуму запису W */
    int read_quorum;       /* Розмір кворуму читання R */
    double net_latency_ms; /* Базова затримка мережі (RTT) */
    double node_fail_prob; /* Ймовірність відмови вузла */
} ArchConfig;

/* Результати оцінювання сценаріїв якості */
typedef struct {
    double write_latency_p99_ms;
    double staleness_rate_pct;
    double write_availability_pct;
    bool is_latency_risk;
    bool is_consistency_risk;
    bool is_tradeoff_point;
} EvaluationResult;

/* Генератор випадкових чисел для розподілу затримок з джитером */
static double rand_normal(double mean, double stddev) {
    double u1 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double u2 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double z = sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
    double val = mean + z * stddev;
    return val > 0.1 ? val : 0.1;
}

/* Функція порівняння для швидкого сортування qsort */
static int compare_doubles(const void *a, const void *b) {
    double arg1 = *(const double *)a;
    double arg2 = *(const double *)b;
    if (arg1 < arg2) return -1;
    if (arg1 > arg2) return 1;
    return 0;
}

/* Оцінка одного прогону архітектурної конфігурації за методом Монте-Карло */
EvaluationResult evaluate_architecture(const ArchConfig *cfg) {
    EvaluationResult res = {0};
    double latencies[NUM_TRIALS];
    int stale_reads_count = 0;
    int failed_writes_count = 0;

    for (int t = 0; t < NUM_TRIALS; t++) {
        /* Симуляція стану вузлів (доступний чи збійний) */
        bool node_alive[MAX_NODES];
        double node_lat[MAX_NODES];
        int alive_count = 0;

        for (int i = 0; i < cfg->total_nodes; i++) {
            double r = (double)rand() / (double)RAND_MAX;
            node_alive[i] = (r >= cfg->node_fail_prob);
            if (node_alive[i]) {
                alive_count++;
                node_lat[i] = rand_normal(cfg->net_latency_ms, cfg->net_latency_ms * 0.35);
            } else {
                node_lat[i] = 1e9; /* Вузол недоступний через збій */
            }
        }

        /* 1. Оцінка доступності та затримки запису */
        if (alive_count < cfg->write_quorum) {
            failed_writes_count++;
            latencies[t] = 100.0; /* Штраф за таймаут операції */
            continue;
        }

        /* Визначаємо час відповіді W-го найшвидшого працездатного вузла */
        double alive_lat[MAX_NODES];
        int k = 0;
        for (int i = 0; i < cfg->total_nodes; i++) {
            if (node_alive[i]) {
                alive_lat[k++] = node_lat[i];
            }
        }
        qsort(alive_lat, k, sizeof(double), compare_doubles);
        latencies[t] = alive_lat[cfg->write_quorum - 1];

        /* 2. Оцінка узгодженості: перевірка перетину кворумів запису та читання */
        if (cfg->write_quorum + cfg->read_quorum <= cfg->total_nodes) {
            /* Кворуми не перетинаються гарантовано: існує ймовірність читання з незаписаних вузлів */
            int non_updated_nodes = cfg->total_nodes - cfg->write_quorum;
            if (cfg->read_quorum <= non_updated_nodes) {
                double p_stale = 1.0;
                for (int step = 0; step < cfg->read_quorum; step++) {
                    p_stale *= (double)(non_updated_nodes - step) / (double)(cfg->total_nodes - step);
                }
                if (((double)rand() / (double)RAND_MAX) < p_stale) {
                    stale_reads_count++;
                }
            }
        }
    }

    /* Розрахунок 99-го перцентиля затримки */
    qsort(latencies, NUM_TRIALS, sizeof(double), compare_doubles);
    int p99_idx = (int)(NUM_TRIALS * 0.99);
    res.write_latency_p99_ms = latencies[p99_idx];
    res.staleness_rate_pct = ((double)stale_reads_count / (double)NUM_TRIALS) * 100.0;
    res.write_availability_pct = (1.0 - (double)failed_writes_count / (double)NUM_TRIALS) * 100.0;

    /* Класифікація результатів за правилами ATAM */
    res.is_latency_risk = (res.write_latency_p99_ms > 4.0);
    res.is_consistency_risk = (res.staleness_rate_pct > 0.0001);
    res.is_tradeoff_point = (cfg->write_quorum > 1 && cfg->write_quorum + cfg->read_quorum > cfg->total_nodes);

    return res;
}

int main(void) {
    srand(42);
    printf("=== ATAM Architecture Evaluation Harness (C99) ===\n\n");
    printf("N=5 вузлів, Базова RTT = 1.5 мс, Ймовірність збою вузла = 5%%\n");
    printf("----------------------------------------------------------------------------------\n");
    printf(" Конфігурація (W, R) | Latency p99 | Stale Reads | Availability | ATAM Вердикт    \n");
    printf("----------------------------------------------------------------------------------\n");

    int test_configs[4][2] = {
        {1, 1}, /* Асинхронний запис, слабке читання */
        {1, 3}, /* Швидкий запис, без перетину */
        {3, 3}, /* Строгий кворум більшості (W+R=6 > 5) */
        {5, 1}  /* All-Ack запис у всі вузли */
    };

    for (int i = 0; i < 4; i++) {
        ArchConfig cfg = {
            .total_nodes = 5,
            .write_quorum = test_configs[i][0],
            .read_quorum = test_configs[i][1],
            .net_latency_ms = 1.5,
            .node_fail_prob = 0.05
        };

        EvaluationResult r = evaluate_architecture(&cfg);

        char verdict[64];
        if (r.is_consistency_risk && !r.is_latency_risk) {
            snprintf(verdict, sizeof(verdict), "РИЗИК (Консистентність)");
        } else if (r.is_latency_risk) {
            snprintf(verdict, sizeof(verdict), "РИЗИК (Затримка SLA)");
        } else if (r.is_tradeoff_point) {
            snprintf(verdict, sizeof(verdict), "ТОЧКА КОМПРОМІСУ (NR)");
        } else {
            snprintf(verdict, sizeof(verdict), "НЕ-РИЗИК");
        }

        printf(" W=%d, R=%d           |   %5.2f ms  |   %5.2f %%   |   %6.2f %%   | %s\n",
               cfg.write_quorum, cfg.read_quorum,
               r.write_latency_p99_ms, r.staleness_rate_pct, r.write_availability_pct,
               verdict);
    }
    printf("----------------------------------------------------------------------------------\n");
    return 0;
}
