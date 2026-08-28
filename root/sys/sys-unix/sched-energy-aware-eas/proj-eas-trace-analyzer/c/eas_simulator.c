/* eas_simulator.c — Реалізація мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_OPP 4
#define SCHED_CAPACITY_SCALE 1024

typedef struct {
    unsigned long frequency_khz;
    unsigned long power_mw;
    unsigned long performance;
} opp_entry_t;

typedef struct {
    const char *name;
    unsigned long capacity_orig;
    int num_opp;
    opp_entry_t opps[MAX_OPP];
} perf_domain_t;

static perf_domain_t little_domain = {
    .name = "LITTLE Cluster",
    .capacity_orig = 400,
    .num_opp = 3,
    .opps = {
        { 300000,  45, 100 },
        { 600000,  95, 200 },
        { 1200000, 210, 400 }
    }
};

static perf_domain_t big_domain = {
    .name = "big Cluster",
    .capacity_orig = 1024,
    .num_opp = 3,
    .opps = {
        { 800000,  450, 500 },
        { 1500000, 900, 800 },
        { 2000000, 1500, 1024 }
    }
};

static unsigned long get_domain_power(const perf_domain_t *domain, unsigned long util_request) {
    if (util_request == 0) {
        return 0;
    }
    /* Розрахунок вимоги з урахуванням headroom 1.25 */
    unsigned long req = (util_request * 125) / 100;
    if (req > domain->capacity_orig) {
        req = domain->capacity_orig;
    }

    for (int i = 0; i < domain->num_opp; i++) {
        if (domain->opps[i].performance >= req) {
            return domain->opps[i].power_mw;
        }
    }
    return domain->opps[domain->num_opp - 1].power_mw;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Використання: %s <util_little> <util_big> <task_util>\n", argv[0]);
        return 1;
    }

    unsigned long util_little = strtoul(argv[1], NULL, 10);
    unsigned long util_big = strtoul(argv[2], NULL, 10);
    unsigned long task_util = strtoul(argv[3], NULL, 10);

    /* 1. Поточне енергоспоживання системи */
    unsigned long p_little_cur = get_domain_power(&little_domain, util_little);
    unsigned long p_big_cur = get_domain_power(&big_domain, util_big);
    unsigned long e_current = p_little_cur + p_big_cur;

    /* 2. Варіант А: Задача на LITTLE */
    unsigned long p_little_candA = get_domain_power(&little_domain, util_little + task_util);
    unsigned long p_big_candA = p_big_cur;
    unsigned long e_candA = p_little_candA + p_big_candA;
    long delta_A = (long)e_candA - (long)e_current;

    /* 3. Варіант Б: Задача на big */
    unsigned long p_little_candB = p_little_cur;
    unsigned long p_big_candB = get_domain_power(&big_domain, util_big + task_util);
    unsigned long e_candB = p_little_candB + p_big_candB;
    long delta_B = (long)e_candB - (long)e_current;

    printf("=== Симуляція рішень EAS (C) ===\n");
    printf("Поточне споживання системи: %lu мВт\n", e_current);
    printf("Варіант А (на LITTLE): Споживання = %lu мВт, ΔE = %+ld мВт\n", e_candA, delta_A);
    printf("Варіант Б (на big):    Споживання = %lu мВт, ΔE = %+ld мВт\n", e_candB, delta_B);

    if (delta_A < delta_B) {
        printf("Висновок: Призначити задачу на ядро LITTLE (заощадження %ld мВт)\n", delta_B - delta_A);
    } else {
        printf("Висновок: Призначити задачу на ядро big (заощадження %ld мВт)\n", delta_A - delta_B);
    }

    return 0;
}
