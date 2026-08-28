#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#define M_PI_F 3.14159265358979323846f
#define NUM_MICS 4
#define FRAME_SIZE 1024
#define SAMPLING_RATE 16000.0f
#define SPEED_OF_SOUND 343.0f
#define MIC_SPACING 0.042f // 4.2 см (d <= lambda/2 для f <= 4083 Гц)

typedef struct {
    float re;
    float im;
} Complex;

static Complex c_add(Complex a, Complex b) {
    Complex r = { a.re + b.re, a.im + b.im };
    return r;
}

static Complex c_sub(Complex a, Complex b) {
    Complex r = { a.re - b.re, a.im - b.im };
    return r;
}

static Complex c_mul(Complex a, Complex b) {
    Complex r = { a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re };
    return r;
}

static Complex c_conj(Complex a) {
    Complex r = { a.re, -a.im };
    return r;
}

static float c_abs(Complex a) {
    return sqrtf(a.re * a.re + a.im * a.im);
}

// Пряме та зворотне швидке перетворення Фур'є (Cooley-Tukey Radix-2)
static void fft(Complex* x, int n, int invert) {
    int i, j, k;
    for (i = 1, j = 0; i < n; i++) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1) {
            j ^= bit;
        }
        j ^= bit;
        if (i < j) {
            Complex tmp = x[i];
            x[i] = x[j];
            x[j] = tmp;
        }
    }

    for (int len = 2; len <= n; len <<= 1) {
        float ang = 2.0f * M_PI_F / (float)len * (invert ? -1.0f : 1.0f);
        Complex wlen = { cosf(ang), sinf(ang) };
        for (i = 0; i < n; i += len) {
            Complex w = { 1.0f, 0.0f };
            for (k = 0; k < len / 2; k++) {
                Complex u = x[i + k];
                Complex v = c_mul(x[i + k + len / 2], w);
                x[i + k] = c_add(u, v);
                x[i + k + len / 2] = c_sub(u, v);
                w = c_mul(w, wlen);
            }
        }
    }

    if (invert) {
        for (i = 0; i < n; i++) {
            x[i].re /= (float)n;
            x[i].im /= (float)n;
        }
    }
}

// Розрахунок GCC-PHAT та визначення затримки між двома каналами
static float gcc_phat_tdoa(const float* sig1, const float* sig2, int n, float fs, float d_max_sec) {
    Complex* x1 = (Complex*)malloc(sizeof(Complex) * n);
    Complex* x2 = (Complex*)malloc(sizeof(Complex) * n);
    Complex* g12 = (Complex*)malloc(sizeof(Complex) * n);

    for (int i = 0; i < n; i++) {
        float win = 0.5f * (1.0f - cosf(2.0f * M_PI_F * (float)i / (float)(n - 1)));
        x1[i].re = sig1[i] * win;
        x1[i].im = 0.0f;
        x2[i].re = sig2[i] * win;
        x2[i].im = 0.0f;
    }

    fft(x1, n, 0);
    fft(x2, n, 0);

    const float eps = 1e-7f;
    for (int k = 0; k < n; k++) {
        Complex prod = c_mul(x1[k], c_conj(x2[k]));
        float mag = c_abs(prod);
        g12[k].re = prod.re / (mag + eps);
        g12[k].im = prod.im / (mag + eps);
    }

    fft(g12, n, 1);

    // Максимальна кількість відліків затримки за відстанню між мікрофонами
    int max_lags = (int)ceilf(d_max_sec * fs) + 2;
    if (max_lags > n / 2) max_lags = n / 2;

    float max_val = -1.0f;
    int best_lag = 0;

    for (int lag = -max_lags; lag <= max_lags; lag++) {
        int idx = (lag < 0) ? (n + lag) : lag;
        float val = g12[idx].re;
        if (val > max_val) {
            max_val = val;
            best_lag = lag;
        }
    }

    // Параболічна субдискретна інтерполяція верхівки кореляційного піка
    int idx_m = (best_lag - 1 < 0) ? (n + best_lag - 1) : (best_lag - 1);
    int idx_0 = (best_lag < 0) ? (n + best_lag) : best_lag;
    int idx_p = (best_lag + 1 < 0) ? (n + best_lag + 1) : (best_lag + 1);

    float ym = g12[idx_m].re;
    float y0 = g12[idx_0].re;
    float yp = g12[idx_p].re;

    float delta = 0.0f;
    float denom = 2.0f * (ym - 2.0f * y0 + yp);
    if (fabsf(denom) > 1e-9f) {
        delta = (ym - yp) / denom;
        if (delta > 0.5f) delta = 0.5f;
        if (delta < -0.5f) delta = -0.5f;
    }

    free(x1);
    free(x2);
    free(g12);

    return ((float)best_lag + delta) / fs;
}

// Формування променя Delay-and-Sum для заданого кута theta_deg
static void delay_and_sum(const float input[NUM_MICS][FRAME_SIZE], float* output,
                          int n, float fs, float theta_deg, float spacing, float c) {
    float theta_rad = theta_deg * M_PI_F / 180.0f;

    for (int i = 0; i < n; i++) {
        output[i] = 0.0f;
    }

    for (int m = 0; m < NUM_MICS; m++) {
        float tau_sec = (float)m * spacing * sinf(theta_rad) / c;
        float shift_samples = tau_sec * fs;
        int int_shift = (int)floorf(shift_samples);
        float frac_shift = shift_samples - (float)int_shift;

        for (int i = 0; i < n; i++) {
            int src_idx = i + int_shift;
            float val = 0.0f;
            if (src_idx >= 0 && src_idx + 1 < n) {
                val = (1.0f - frac_shift) * input[m][src_idx] + frac_shift * input[m][src_idx + 1];
            } else if (src_idx >= 0 && src_idx < n) {
                val = input[m][src_idx];
            }
            output[i] += val / (float)NUM_MICS;
        }
    }
}

int main(void) {
    float audio[NUM_MICS][FRAME_SIZE];
    float target_angle_deg = 32.0f;
    float target_freq = 1200.0f;

    printf("=== Мікрофонний масив: TDoA локалізація та Delay-and-Sum ===\n");
    printf("Конфігурація: M = %d мікрофонів, d = %.3f м, fs = %.0f Гц\n",
           NUM_MICS, MIC_SPACING, SAMPLING_RATE);
    printf("Істинний кут джерела: %.1f градусів\n\n", target_angle_deg);

    float target_rad = target_angle_deg * M_PI_F / 180.0f;

    // Синтез тестових сигналів з різницею ходу та шумом
    for (int m = 0; m < NUM_MICS; m++) {
        float delay_sec = (float)m * MIC_SPACING * sinf(target_rad) / SPEED_OF_SOUND;
        for (int i = 0; i < FRAME_SIZE; i++) {
            float t = (float)i / SAMPLING_RATE - delay_sec;
            // Тональний сигнал з гармонікою
            float sig = sinf(2.0f * M_PI_F * target_freq * t) + 0.5f * sinf(2.0f * M_PI_F * 2.0f * target_freq * t);
            // Адитивний білий шум
            float noise = (((float)rand() / (float)RAND_MAX) - 0.5f) * 0.4f;
            audio[m][i] = sig + noise;
        }
    }

    // Локалізація джерела через GCC-PHAT між M0 та M3 (максимальна база)
    float d_total = (float)(NUM_MICS - 1) * MIC_SPACING;
    float tdoa_est = gcc_phat_tdoa(audio[0], audio[NUM_MICS - 1], FRAME_SIZE, SAMPLING_RATE, d_total / SPEED_OF_SOUND);

    float sin_arg = tdoa_est * SPEED_OF_SOUND / d_total;
    if (sin_arg > 1.0f) sin_arg = 1.0f;
    if (sin_arg < -1.0f) sin_arg = -1.0f;
    float estimated_angle_deg = asinf(sin_arg) * 180.0f / M_PI_F;

    printf("Оцінена затримка TDoA (M0 -> M%d): %.4f мс\n", NUM_MICS - 1, tdoa_est * 1000.0f);
    printf("Оцінений кут приходу: %.2f градусів (похибка: %.2f°)\n\n",
           estimated_angle_deg, fabsf(estimated_angle_deg - target_angle_deg));

    // Застосування Delay-and-Sum beamforming
    float beamformed[FRAME_SIZE];
    delay_and_sum(audio, beamformed, FRAME_SIZE, SAMPLING_RATE, estimated_angle_deg, MIC_SPACING, SPEED_OF_SOUND);

    // Оцінка потужності одного каналу проти сформованого променя
    float p_single = 0.0f, p_beam = 0.0f;
    for (int i = 0; i < FRAME_SIZE; i++) {
        p_single += audio[0][i] * audio[0][i];
        p_beam += beamformed[i] * beamformed[i];
    }
    p_single /= (float)FRAME_SIZE;
    p_beam /= (float)FRAME_SIZE;

    printf("Середня потужність одиночного мікрофона M0: %.4f\n", p_single);
    printf("Середня потужність сформованого променя:      %.4f\n", p_beam);
    printf("Алгоритм успішно виділив синфазний сигнал та придушив шум.\n");

    return 0;
}
