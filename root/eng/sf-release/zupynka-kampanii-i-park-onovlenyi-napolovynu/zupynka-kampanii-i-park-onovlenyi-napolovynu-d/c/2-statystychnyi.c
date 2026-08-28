#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

typedef struct {
    double value;
    int is_canary;
} sample_entry_t;

static int compare_entries(const void *a, const void *b) {
    const sample_entry_t *ea = (const sample_entry_t *)a;
    const sample_entry_t *eb = (const sample_entry_t *)b;
    if (ea->value < eb->value) return -1;
    if (ea->value > eb->value) return 1;
    return 0;
}

/* Обчислення рангової U-статистики Манна-Вітні для двох вибірок затримок */
bool evaluate_canary_mann_whitney(const double *baseline, size_t n,
                                  const double *canary, size_t m,
                                  double *out_u_stat, double *out_z_score,
                                  double *out_p_val) {
    if (!baseline || !canary || n == 0 || m == 0 || !out_u_stat || !out_z_score) {
        return false;
    }

    size_t total_n = n + m;
    sample_entry_t *samples = (sample_entry_t *)malloc(total_n * sizeof(sample_entry_t));
    if (!samples) return false;

    for (size_t i = 0; i < n; ++i) {
        samples[i].value = baseline[i];
        samples[i].is_canary = 0;
    }
    for (size_t j = 0; j < m; ++j) {
        samples[n + j].value = canary[j];
        samples[n + j].is_canary = 1;
    }

    qsort(samples, total_n, sizeof(sample_entry_t), compare_entries);

    /* Ранжування з корекцією зв'язаних рангів (ties resolution) */
    double *assigned_ranks = (double *)malloc(total_n * sizeof(double));
    if (!assigned_ranks) {
        free(samples);
        return false;
    }

    size_t idx = 0;
    while (idx < total_n) {
        size_t end_idx = idx;
        while (end_idx + 1 < total_n && samples[end_idx + 1].value == samples[idx].value) {
            end_idx++;
        }
        double mean_rank = 1.0 + (double)(idx + end_idx) / 2.0;
        for (size_t size_k = idx; size_k <= end_idx; ++size_k) {
            assigned_ranks[size_k] = mean_rank;
        }
        idx = end_idx + 1;
    }

    double r_baseline = 0.0;
    for (size_t i = 0; i < total_n; ++i) {
        if (samples[i].is_canary == 0) {
            r_baseline += assigned_ranks[i];
        }
    }

    double dn = (double)n;
    double dm = (double)m;
    double u1 = dn * dm + (dn * (dn + 1.0)) / 2.0 - r_baseline;
    double u2 = dn * dm - u1;
    double u_min = (u1 < u2) ? u1 : u2;

    double mu_u = (dn * dm) / 2.0;
    double sigma_u = sqrt((dn * dm * (dn + dm + 1.0)) / 12.0);

    *out_u_stat = u_min;
    if (sigma_u > 1e-7) {
        *out_z_score = (u_min - mu_u) / sigma_u;
    } else {
        *out_z_score = 0.0;
    }

    if (out_p_val) {
        *out_p_val = erfc(fabs(*out_z_score) / sqrt(2.0));
    }

    free(assigned_ranks);
    free(samples);
    return true;
}
