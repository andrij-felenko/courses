#include <stdio.h>
#include <stdint.h>
#include <math.h>

typedef struct {
    uint64_t count;
    double mean;
    double M2;
} welford_t;

void welford_init(welford_t *acc) {
    acc->count = 0;
    acc->mean = 0.0;
    acc->M2 = 0.0;
}

void welford_update(welford_t *acc, double x) {
    acc->count++;
    double delta = x - acc->mean;
    acc->mean += delta / (double)acc->count;
    double delta2 = x - acc->mean;
    acc->M2 += delta * delta2;
}

double welford_variance(const welford_t *acc) {
    if (acc->count < 2) return 0.0;
    return acc->M2 / (double)(acc->count - 1);
}

double welford_stddev(const welford_t *acc) {
    return sqrt(welford_variance(acc));
}
