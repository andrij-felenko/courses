#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <float.h>

/* Обчислення LLR для одного відліку BPSK */
double bpsk_llr_sample(double y, double sigma2) {
    if (sigma2 <= 1e-12) {
        return (y >= 0.0) ? 1000.0 : -1000.0;
    }
    return 2.0 * y / sigma2;
}

/* М'який демодулятор BPSK для масиву відліків */
void demap_bpsk(const double *y, const double *l_prior, double *l_post,
                size_t num_bits, double sigma2) {
    double scale = 2.0 / (sigma2 > 1e-12 ? sigma2 : 1e-12);
    for (size_t i = 0; i < num_bits; i++) {
        double l_ch = y[i] * scale;
        double prior = (l_prior != NULL) ? l_prior[i] : 0.0;
        l_post[i] = l_ch + prior;
    }
}

/* Демодулятор QPSK (Грей): 1 комплексний символ -> 2 LLR бітів */
void demap_qpsk(const double *y_i, const double *y_q, double *l_out,
                size_t num_symbols, double sigma2) {
    double scale = 2.0 * sqrt(2.0) / (sigma2 > 1e-12 ? sigma2 : 1e-12);
    for (size_t i = 0; i < num_symbols; i++) {
        l_out[2 * i]     = y_i[i] * scale;  /* Біт 0 (In-phase sign) */
        l_out[2 * i + 1] = y_q[i] * scale;  /* Біт 1 (Quadrature sign) */
    }
}

/* Демодулятор 16-QAM (Max-Log, Грей): 1 комплексний символ -> 4 LLR бітів */
void demap_16qam_maxlog(const double *y_i, const double *y_q, double *l_out,
                        size_t num_symbols, double sigma2) {
    double safe_sigma2 = (sigma2 > 1e-12) ? sigma2 : 1e-12;
    double sqrt10 = sqrt(10.0);
    double c1 = 4.0 * sqrt10 / safe_sigma2;
    double c2 = 2.0 * sqrt10 / safe_sigma2;
    double threshold = 2.0 / sqrt10;

    for (size_t i = 0; i < num_symbols; i++) {
        double yi = y_i[i];
        double yq = y_q[i];

        /* Синфазна вісь I */
        l_out[4 * i + 0] = c1 * yi;
        l_out[4 * i + 1] = c2 * (threshold - fabs(yi));

        /* Квадратурна вісь Q */
        l_out[4 * i + 2] = c1 * yq;
        l_out[4 * i + 3] = c2 * (threshold - fabs(yq));
    }
}

/* Вузол перевірки парності Min-Sum для LDPC декодера (обновлення L_ext) */
void ldpc_min_sum_check_node(const double *l_in, double *l_ext_out, size_t degree) {
    if (degree < 2) return;

    /* Обчислення загального добутку знаків та двох найменших модулів */
    int global_sign = 1;
    double min1 = DBL_MAX;
    double min2 = DBL_MAX;
    size_t min1_idx = 0;

    for (size_t i = 0; i < degree; i++) {
        if (l_in[i] < 0.0) {
            global_sign = -global_sign;
        }
        double abs_val = fabs(l_in[i]);
        if (abs_val < min1) {
            min2 = min1;
            min1 = abs_val;
            min1_idx = i;
        } else if (abs_val < min2) {
            min2 = abs_val;
        }
    }

    /* Формування вихідного LLR для кожного ребра */
    for (size_t i = 0; i < degree; i++) {
        int edge_sign = (l_in[i] < 0.0) ? -global_sign : global_sign;
        double min_mag = (i == min1_idx) ? min2 : min1;
        l_ext_out[i] = (double)edge_sign * min_mag;
    }
}

/* Квантизація LLR у 8-бітне ціле зі знаком [-127, 127] */
int8_t quantize_llr(double llr, double scale_factor) {
    double scaled = llr * scale_factor;
    if (scaled > 127.0) return 127;
    if (scaled < -127.0) return -127;
    return (int8_t)round(scaled);
}
