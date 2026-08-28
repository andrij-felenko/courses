#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double alpha;
    double dh0_oe;
} fmr_fit_result_t;

double fmr_kittel_inplane(double freq_ghz, double ms_ka_m, double g_factor) {
    double ms_a_m = ms_ka_m * 1000.0;
    double gamma_ghz_t = (g_factor * 1.760859e11) / (2.0 * M_PI * 1e9);
    double mu0_ms = 4.0 * M_PI * 1e-7 * ms_a_m;
    double f_g = freq_ghz / gamma_ghz_t;
    double b_r = (-mu0_ms + sqrt(mu0_ms * mu0_ms + 4.0 * f_g * f_g)) / 2.0;
    return b_r * 10000.0;
}

int fmr_fit_gilbert(const double* freqs_ghz, const double* linewidths_oe, size_t count,
                    double g_factor, fmr_fit_result_t* out_result) {
    if (!freqs_ghz || !linewidths_oe || !out_result || count < 2) {
        return -1;
    }

    double sum_f = 0.0, sum_dh = 0.0, sum_ff = 0.0, sum_fdh = 0.0;
    for (size_t i = 0; i < count; ++i) {
        sum_f += freqs_ghz[i];
        sum_dh += linewidths_oe[i];
        sum_ff += freqs_ghz[i] * freqs_ghz[i];
        sum_fdh += freqs_ghz[i] * linewidths_oe[i];
    }

    double denom = (count * sum_ff - sum_f * sum_f);
    if (fabs(denom) < 1e-12) return -2;

    double slope = (count * sum_fdh - sum_f * sum_dh) / denom;
    double dh0 = (sum_dh - slope * sum_f) / (double)count;
    double gamma_ghz_t = (g_factor * 1.760859e11) / (2.0 * M_PI * 1e9);

    out_result->alpha = (slope * gamma_ghz_t) / 2000.0;
    out_result->dh0_oe = dh0;
    return 0;
}

int main(void) {
    double freqs[] = {4.0, 8.0, 12.0, 16.0, 20.0};
    double dhs[] = {6.2, 8.1, 10.0, 11.9, 13.8};
    size_t count = sizeof(freqs) / sizeof(freqs[0]);

    fmr_fit_result_t fit;
    if (fmr_fit_gilbert(freqs, dhs, count, 2.08, &fit) == 0) {
        printf("FMR C Analysis Results:\n");
        printf("Alpha (Gilbert): %.6f\n", fit.alpha);
        printf("Delta H0: %.2f Oe\n", fit.dh0_oe);
    } else {
        printf("Fitting error occurred.\n");
    }
    return 0;
}
