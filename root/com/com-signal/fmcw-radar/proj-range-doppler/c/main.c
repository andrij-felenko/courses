#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    float real;
    float imag;
} Complex32;

typedef struct {
    float range_m;       /* Дальність до цілі, м */
    float velocity_ms;   /* Радіальна швидкість цілі, м/с */
    float power_db;      /* Потужність сигналу, дБ */
    int range_bin;       /* Індекс біна дальності */
    int doppler_bin;     /* Індекс біна швидкості */
} RadarTarget;

/* Ініціалізація вікна Ганнінга */
void init_hanning_window(float *win, int n) {
    for (int i = 0; i < n; i++) {
        win[i] = 0.5f * (1.0f - cosf((2.0f * (float)M_PI * (float)i) / (float)(n - 1)));
    }
}

/* Ітеративне БПФ з проріджуванням за часом (Radix-2 Cooley-Tukey) */
void fft_radix2(Complex32 *x, int n, bool invert) {
    /* Перестановка з біт-реверсивною адресацією */
    int j = 0;
    for (int i = 0; i < n - 1; i++) {
        if (i < j) {
            Complex32 temp = x[i];
            x[i] = x[j];
            x[j] = temp;
        }
        int k = n >> 1;
        while (k <= j) {
            j -= k;
            k >>= 1;
        }
        j += k;
    }

    /* Метелики БПФ */
    for (int len = 2; len <= n; len <<= 1) {
        float angle = (invert ? 2.0f : -2.0f) * (float)M_PI / (float)len;
        Complex32 wlen = { cosf(angle), sinf(angle) };
        for (int i = 0; i < n; i += len) {
            Complex32 w = { 1.0f, 0.0f };
            for (int k = 0; k < len / 2; k++) {
                Complex32 u = x[i + k];
                Complex32 v = {
                    w.real * x[i + k + len / 2].real - w.imag * x[i + k + len / 2].imag,
                    w.real * x[i + k + len / 2].imag + w.imag * x[i + k + len / 2].real
                };
                x[i + k].real = u.real + v.real;
                x[i + k].imag = u.imag + v.imag;
                x[i + k + len / 2].real = u.real - v.real;
                x[i + k + len / 2].imag = u.imag - v.imag;

                float next_w_real = w.real * wlen.real - w.imag * wlen.imag;
                w.imag = w.real * wlen.imag + w.imag * wlen.real;
                w.real = next_w_real;
            }
        }
    }

    if (invert) {
        for (int i = 0; i < n; i++) {
            x[i].real /= (float)n;
            x[i].imag /= (float)n;
        }
    }
}

/* Двовимірна 2D-FFT обробка радарного кадру */
void process_radar_cube_2dfft(Complex32 *cube, float *rd_map_power,
                             int n_chirps, int n_samples) {
    float *win_fast = (float*)malloc(sizeof(float) * n_samples);
    float *win_slow = (float*)malloc(sizeof(float) * n_chirps);
    init_hanning_window(win_fast, n_samples);
    init_hanning_window(win_slow, n_chirps);

    /* 1. Range-FFT по рядках (швидкий час) */
    Complex32 *row_buf = (Complex32*)malloc(sizeof(Complex32) * n_samples);
    for (int c = 0; c < n_chirps; c++) {
        for (int s = 0; s < n_samples; s++) {
            int idx = c * n_samples + s;
            row_buf[s].real = cube[idx].real * win_fast[s];
            row_buf[s].imag = cube[idx].imag * win_fast[s];
        }
        fft_radix2(row_buf, n_samples, false);
        for (int s = 0; s < n_samples; s++) {
            cube[c * n_samples + s] = row_buf[s];
        }
    }
    free(row_buf);

    /* 2. Doppler-FFT по стовпчиках (повільний час) */
    Complex32 *col_buf = (Complex32*)malloc(sizeof(Complex32) * n_chirps);
    for (int s = 0; s < n_samples; s++) {
        for (int c = 0; c < n_chirps; c++) {
            int idx = c * n_samples + s;
            col_buf[c].real = cube[idx].real * win_slow[c];
            col_buf[c].imag = cube[idx].imag * win_slow[c];
        }
        fft_radix2(col_buf, n_chirps, false);

        /* 3. Центрування спектра (FFTShift) та розрахунок потужності */
        for (int c = 0; c < n_chirps; c++) {
            int shifted_c = (c + n_chirps / 2) % n_chirps;
            float mag2 = col_buf[c].real * col_buf[c].real + col_buf[c].imag * col_buf[c].imag;
            rd_map_power[s * n_chirps + shifted_c] = mag2;
        }
    }
    free(col_buf);
    free(win_fast);
    free(win_slow);
}

/* 2D CA-CFAR детектор цілей */
int detect_cfar_2d(const float *rd_map_power, int n_samples, int n_chirps,
                   int guard_r, int guard_d, int train_r, int train_d,
                   float p_fa, float range_res_m, float vel_res_ms,
                   RadarTarget *out_targets, int max_targets) {
    int count = 0;
    int n_train_cells = (2 * (train_r + guard_r) + 1) * (2 * (train_d + guard_d) + 1)
                      - (2 * guard_r + 1) * (2 * guard_d + 1);

    /* Масштабний коефіцієнт порогу за заданою ймовірністю P_fa */
    float alpha = (float)n_train_cells * (powf(p_fa, -1.0f / (float)n_train_cells) - 1.0f);

    int r_start = train_r + guard_r;
    int r_end = n_samples - (train_r + guard_r);
    int d_start = train_d + guard_d;
    int d_end = n_chirps - (train_d + guard_d);

    for (int r = r_start; r < r_end; r++) {
        for (int d = d_start; d < d_end; d++) {
            float cut_val = rd_map_power[r * n_chirps + d];

            /* Розрахунок середнього шуму в навчальних комірках */
            float noise_sum = 0.0f;
            for (int dr = -(train_r + guard_r); dr <= (train_r + guard_r); dr++) {
                for (int dd = -(train_d + guard_d); dd <= (train_d + guard_d); dd++) {
                    if (abs(dr) <= guard_r && abs(dd) <= guard_d) {
                        continue; /* Пропуск охоронної зони і CUT */
                    }
                    noise_sum += rd_map_power[(r + dr) * n_chirps + (d + dd)];
                }
            }
            float noise_avg = noise_sum / (float)n_train_cells;
            float threshold = alpha * noise_avg;

            if (cut_val > threshold) {
                /* Придушення не-максимумів: перевірка на локальний пік */
                bool is_peak = true;
                for (int dr = -guard_r; dr <= guard_r && is_peak; dr++) {
                    for (int dd = -guard_d; dd <= guard_d; dd++) {
                        if (dr == 0 && dd == 0) continue;
                        if (rd_map_power[(r + dr) * n_chirps + (d + dd)] >= cut_val) {
                            is_peak = false;
                            break;
                        }
                    }
                }

                if (is_peak && count < max_targets) {
                    out_targets[count].range_bin = r;
                    out_targets[count].doppler_bin = d;
                    out_targets[count].range_m = (float)r * range_res_m;
                    out_targets[count].velocity_ms = (float)(d - n_chirps / 2) * vel_res_ms;
                    out_targets[count].power_db = 10.0f * log10f(cut_val + 1e-12f);
                    count++;
                }
            }
        }
    }
    return count;
}
