#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

typedef enum {
    SOURCE_SINGLE_PHOTON,
    SOURCE_COHERENT,
    SOURCE_THERMAL
} source_type_t;

typedef struct {
    int bins;
    double dt_ns;
    int* counts_a;
    int* counts_b;
    double* g2;
    int max_lag;
} hbt_simulation_t;

hbt_simulation_t* hbt_create(int bins, double dt_ns, int max_lag) {
    hbt_simulation_t* sim = (hbt_simulation_t*)malloc(sizeof(hbt_simulation_t));
    if (!sim) return NULL;
    sim->bins = bins;
    sim->dt_ns = dt_ns;
    sim->max_lag = max_lag;
    sim->counts_a = (int*)calloc(bins, sizeof(int));
    sim->counts_b = (int*)calloc(bins, sizeof(int));
    sim->g2 = (double*)calloc(max_lag + 1, sizeof(double));
    return sim;
}

void hbt_free(hbt_simulation_t* sim) {
    if (!sim) return;
    free(sim->counts_a);
    free(sim->counts_b);
    free(sim->g2);
    free(sim);
}

void hbt_run(hbt_simulation_t* sim, source_type_t type, double mean_photons) {
    for (int i = 0; i < sim->bins; i++) {
        int n_photons = 0;
        if (type == SOURCE_SINGLE_PHOTON) {
            double r = (double)rand() / RAND_MAX;
            n_photons = (r < mean_photons) ? 1 : 0;
        } else if (type == SOURCE_COHERENT) {
            // Проста ітеративна генерація Пуассона
            double L = exp(-mean_photons);
            int k = 0;
            double p = 1.0;
            do {
                k++;
                p *= (double)rand() / RAND_MAX;
            } while (p > L);
            n_photons = k - 1;
        } else { // THERMAL
            double r = (double)rand() / RAND_MAX;
            n_photons = (int)(-mean_photons * log(1.0 - r + 1e-12));
        }

        // Проходження кожної частинки крізь світлодільник 50/50
        for (int p = 0; p < n_photons; p++) {
            if ((double)rand() / RAND_MAX < 0.5) {
                sim->counts_a[i]++;
            } else {
                sim->counts_b[i]++;
            }
        }
    }
}

void hbt_calculate_g2(hbt_simulation_t* sim) {
    double sum_a = 0.0, sum_b = 0.0;
    for (int i = 0; i < sim->bins; i++) {
        sum_a += sim->counts_a[i];
        sum_b += sim->counts_b[i];
    }
    double mean_a = sum_a / sim->bins;
    double mean_b = sum_b / sim->bins;
    double norm = mean_a * mean_b;

    if (norm < 1e-12) return;

    for (int lag = 0; lag <= sim->max_lag; lag++) {
        double correlation_sum = 0.0;
        int valid_pairs = 0;
        for (int i = 0; i < sim->bins - lag; i++) {
            correlation_sum += (double)sim->counts_a[i] * sim->counts_b[i + lag];
            valid_pairs++;
        }
        double avg_corr = correlation_sum / valid_pairs;
        sim->g2[lag] = avg_corr / norm;
    }
}
