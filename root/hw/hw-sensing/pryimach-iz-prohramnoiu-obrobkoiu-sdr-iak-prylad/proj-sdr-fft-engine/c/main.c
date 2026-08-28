#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    float i;
    float q;
} complex_sample_t;

typedef struct {
    size_t size;
    float *window;
    complex_sample_t *twiddles;
    complex_sample_t *fft_buffer;
    float *power_spectrum_dbm;
    float *averaged_spectrum;
    float cal_offset_db;
    float alpha;
} sdr_spectrum_analyzer_t;

/* Генерація коефіцієнтів 4-точкового вікна Blackman-Harris */
static void init_blackman_harris(float *w, size_t n) {
    const float a0 = 0.35875f;
    const float a1 = 0.48829f;
    const float a2 = 0.14128f;
    const float a3 = 0.01168f;
    for (size_t i = 0; i < n; ++i) {
        float theta = (2.0f * (float)M_PI * (float)i) / (float)(n - 1);
        w[i] = a0 - a1 * cosf(theta) + a2 * cosf(2.0f * theta) - a3 * cosf(3.0f * theta);
    }
}

/* Попередня генерація поворотних множників для прискорення FFT */
static void init_twiddles(complex_sample_t *tw, size_t n) {
    for (size_t i = 0; i < n / 2; ++i) {
        float angle = -2.0f * (float)M_PI * (float)i / (float)n;
        tw[i].i = cosf(angle);
        tw[i].q = sinf(angle);
    }
}

/* Створення та виділення пам'яті аналізатора */
sdr_spectrum_analyzer_t* sdr_analyzer_create(size_t size, float cal_offset_db, float alpha) {
    if ((size & (size - 1)) != 0 || size == 0) {
        return NULL; /* Розмір має бути строго степенем двійки */
    }
    sdr_spectrum_analyzer_t *sa = (sdr_spectrum_analyzer_t*)calloc(1, sizeof(sdr_spectrum_analyzer_t));
    if (!sa) return NULL;

    sa->size = size;
    sa->cal_offset_db = cal_offset_db;
    sa->alpha = alpha;

    sa->window = (float*)malloc(size * sizeof(float));
    sa->twiddles = (complex_sample_t*)malloc((size / 2) * sizeof(complex_sample_t));
    sa->fft_buffer = (complex_sample_t*)malloc(size * sizeof(complex_sample_t));
    sa->power_spectrum_dbm = (float*)malloc(size * sizeof(float));
    sa->averaged_spectrum = (float*)malloc(size * sizeof(float));

    if (!sa->window || !sa->twiddles || !sa->fft_buffer || 
        !sa->power_spectrum_dbm || !sa->averaged_spectrum) {
        free(sa->window);
        free(sa->twiddles);
        free(sa->fft_buffer);
        free(sa->power_spectrum_dbm);
        free(sa->averaged_spectrum);
        free(sa);
        return NULL;
    }

    init_blackman_harris(sa->window, size);
    init_twiddles(sa->twiddles, size);

    for (size_t i = 0; i < size; ++i) {
        sa->averaged_spectrum[i] = -140.0f; /* Ініціалізація рівнем шуму */
    }
    return sa;
}

void sdr_analyzer_destroy(sdr_spectrum_analyzer_t *sa) {
    if (!sa) return;
    free(sa->window);
    free(sa->twiddles);
    free(sa->fft_buffer);
    free(sa->power_spectrum_dbm);
    free(sa->averaged_spectrum);
    free(sa);
}

/* Швидке перетворення Фур'є Radix-2 за часом (in-place) */
static void radix2_fft(complex_sample_t *x, const complex_sample_t *twiddles, size_t n) {
    /* Біт-реверсна перестановка індексів */
    size_t j = 0;
    for (size_t i = 0; i < n - 1; ++i) {
        if (i < j) {
            complex_sample_t temp = x[i];
            x[i] = x[j];
            x[j] = temp;
        }
        size_t k = n >> 1;
        while (k <= j) {
            j -= k;
            k >>= 1;
        }
        j += k;
    }

    /* Каскади метеликів */
    for (size_t len = 2; len <= n; len <<= 1) {
        size_t half_len = len >> 1;
        size_t step = n / len;
        for (size_t i = 0; i < n; i += len) {
            for (size_t m = 0; m < half_len; ++m) {
                complex_sample_t w = twiddles[m * step];
                complex_sample_t u = x[i + m];
                complex_sample_t v = {
                    x[i + m + half_len].i * w.i - x[i + m + half_len].q * w.q,
                    x[i + m + half_len].i * w.q + x[i + m + half_len].q * w.i
                };
                x[i + m].i = u.i + v.i;
                x[i + m].q = u.q + v.q;
                x[i + m + half_len].i = u.i - v.i;
                x[i + m + half_len].q = u.q - v.q;
            }
        }
    }
}

/* Обробка одного блоку комплексних IQ відліків */
void sdr_analyzer_process(sdr_spectrum_analyzer_t *sa, const complex_sample_t *input) {
    const size_t n = sa->size;
    const size_t half = n / 2;

    /* 1. Віконне зважування вхідного блоку */
    for (size_t i = 0; i < n; ++i) {
        sa->fft_buffer[i].i = input[i].i * sa->window[i];
        sa->fft_buffer[i].q = input[i].q * sa->window[i];
    }

    /* 2. Обчислення FFT */
    radix2_fft(sa->fft_buffer, sa->twiddles, n);

    /* 3. fftshift, розрахунок потужності в dBm та відеоусереднення */
    for (size_t i = 0; i < n; ++i) {
        size_t shifted_idx = (i < half) ? (i + half) : (i - half);

        float re = sa->fft_buffer[i].i;
        float im = sa->fft_buffer[i].q;
        float power_lin = re * re + im * im;

        /* Захист від взяття логарифма нуля */
        if (power_lin < 1e-18f) {
            power_lin = 1e-18f;
        }

        float power_dbm = 10.0f * log10f(power_lin) + sa->cal_offset_db;
        sa->power_spectrum_dbm[shifted_idx] = power_dbm;

        /* Експоненційне відеоусереднення */
        sa->averaged_spectrum[shifted_idx] =
            sa->alpha * power_dbm + (1.0f - sa->alpha) * sa->averaged_spectrum[shifted_idx];
    }
}

/* Суббіновий пошук піка за допомогою параболічної інтерполяції */
void sdr_analyzer_find_peak_interp(const sdr_spectrum_analyzer_t *sa, 
                                   float *peak_bin_out, float *peak_power_out) {
    const size_t n = sa->size;
    size_t max_idx = 1;
    float max_val = sa->averaged_spectrum[1];

    for (size_t i = 2; i < n - 1; ++i) {
        if (sa->averaged_spectrum[i] > max_val) {
            max_val = sa->averaged_spectrum[i];
            max_idx = i;
        }
    }

    /* Параболічна інтерполяція по трьох точках */
    float y_left = sa->averaged_spectrum[max_idx - 1];
    float y_mid = sa->averaged_spectrum[max_idx];
    float y_right = sa->averaged_spectrum[max_idx + 1];

    float denom = (y_left - 2.0f * y_mid + y_right);
    float delta = 0.0f;
    if (fabsf(denom) > 1e-6f) {
        delta = 0.5f * (y_left - y_right) / denom;
    }

    *peak_bin_out = (float)max_idx + delta;
    *peak_power_out = y_mid - 0.25f * (y_left - y_right) * delta;
}
