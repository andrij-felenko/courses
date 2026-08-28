#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double real;
    double imag;
} Complex;

typedef struct {
    double *freqs;       /* масив частот для кожного біна (Гц) */
    double *magnitudes;  /* амплітудний спектр */
    double *phases;      /* фазовий спектр (радіани) */
    size_t num_bins;     /* кількість бінів: N / 2 + 1 */
    double fundamental_freq;
    double thd_percent;
} SpectrumResult;

/* Реверс бітів для перестановок на місці */
static size_t bit_reverse(size_t index, size_t log2n) {
    size_t result = 0;
    for (size_t i = 0; i < log2n; ++i) {
        if ((index >> i) & 1) {
            result |= (size_t)1 << (log2n - 1 - i);
        }
    }
    return result;
}

/* Ітеративний Radix-2 FFT (in-place) */
void fft_radix2_c(Complex *data, size_t n) {
    size_t log2n = 0;
    while (((size_t)1 << log2n) < n) log2n++;

    /* 1. Біт-реверсивна перестановка */
    for (size_t i = 0; i < n; ++i) {
        size_t rev = bit_reverse(i, log2n);
        if (i < rev) {
            Complex temp = data[i];
            data[i] = data[rev];
            data[rev] = temp;
        }
    }

    /* 2. Обчислення метеликів за ярусами */
    for (size_t s = 1; s <= log2n; ++s) {
        size_t m = (size_t)1 << s;
        size_t m2 = m >> 1;
        double theta = -2.0 * M_PI / (double)m;
        Complex wm = { cos(theta), sin(theta) };

        for (size_t k = 0; k < n; k += m) {
            Complex w = { 1.0, 0.0 };
            for (size_t j = 0; j < m2; ++j) {
                Complex u = data[k + j];
                Complex t = {
                    w.real * data[k + j + m2].real - w.imag * data[k + j + m2].imag,
                    w.real * data[k + j + m2].imag + w.imag * data[k + j + m2].real
                };
                data[k + j].real = u.real + t.real;
                data[k + j].imag = u.imag + t.imag;
                data[k + j + m2].real = u.real - t.real;
                data[k + j + m2].imag = u.imag - t.imag;

                /* Оновлення множника w */
                double next_w_real = w.real * wm.real - w.imag * wm.imag;
                w.imag = w.real * wm.imag + w.imag * wm.real;
                w.real = next_w_real;
            }
        }
    }
}

/* Повний аналіз спектра дійсного масиву відліків */
SpectrumResult* analyze_spectrum_c(const double *signal, size_t n, double sample_rate) {
    if ((n & (n - 1)) != 0 || n == 0) return NULL; /* N має бути степенем двійки */

    Complex *buf = (Complex*)malloc(n * sizeof(Complex));
    if (!buf) return NULL;

    /* Застосування вікна Ганна для усунення витоку спектра */
    double win_sum = 0.0;
    for (size_t i = 0; i < n; ++i) {
        double w = 0.5 * (1.0 - cos(2.0 * M_PI * (double)i / (double)(n - 1)));
        buf[i].real = signal[i] * w;
        buf[i].imag = 0.0;
        win_sum += w;
    }

    fft_radix2_c(buf, n);

    size_t num_bins = n / 2 + 1;
    SpectrumResult *res = (SpectrumResult*)malloc(sizeof(SpectrumResult));
    res->num_bins = num_bins;
    res->freqs = (double*)malloc(num_bins * sizeof(double));
    res->magnitudes = (double*)malloc(num_bins * sizeof(double));
    res->phases = (double*)malloc(num_bins * sizeof(double));

    double df = sample_rate / (double)n;
    size_t peak_bin = 1;
    double max_mag = 0.0;

    for (size_t k = 0; k < num_bins; ++k) {
        res->freqs[k] = (double)k * df;
        double re = buf[k].real;
        double im = buf[k].imag;
        double raw_mag = sqrt(re * re + im * im);

        /* Нормування амплітуди */
        double mag = (2.0 * raw_mag) / win_sum;
        if (k == 0 || k == n / 2) mag /= 2.0;

        res->magnitudes[k] = mag;
        res->phases[k] = atan2(im, re);

        if (k > 0 && k < n / 2 && mag > max_mag) {
            max_mag = mag;
            peak_bin = k;
        }
    }

    res->fundamental_freq = (double)peak_bin * df;

    /* Розрахунок THD відносно основної знайденої гармоніки */
    double harmonic_sum_sq = 0.0;
    for (size_t h = 2; h <= 10; ++h) {
        size_t h_bin = h * peak_bin;
        if (h_bin < num_bins) {
            double h_mag = res->magnitudes[h_bin];
            harmonic_sum_sq += h_mag * h_mag;
        }
    }
    res->thd_percent = (max_mag > 1e-9) ? (sqrt(harmonic_sum_sq) / max_mag) * 100.0 : 0.0;

    free(buf);
    return res;
}

void free_spectrum_result_c(SpectrumResult *res) {
    if (res) {
        free(res->freqs);
        free(res->magnitudes);
        free(res->phases);
        free(res);
    }
}
