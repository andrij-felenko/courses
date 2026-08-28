/* 
 * DSP модуль моніторингу резонансів Шумана (Мова C)
 * Стандарт: C99 / C11
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define SCHUMANN_FS          256.0f   /* Частота дискретизації (Гц) */
#define SCHUMANN_N           1024     /* Довжина вікна FFT (4 секунди) */
#define M_PI_F               3.14159265358979323846f

/* Структура результату аналізу піку Шумана */
typedef struct {
    float frequency_hz;   /* Визначена центральна частота піку */
    float amplitude_psd;  /* Спектральна густина потужності (пТл²/Гц) */
    float quality_factor; /* Добротність резонансу Q */
    bool  valid;          /* Прапор успішного виявлення */
} SchumannPeak;

typedef struct {
    SchumannPeak peak_n1; /* Перша гармоніка (~7.83 Гц) */
    SchumannPeak peak_n2; /* Друга гармоніка (~14.3 Гц) */
    SchumannPeak peak_n3; /* Третя гармоніка (~20.8 Гц) */
} SchumannReport;

/* Функція застосування вікна Ганна та обчислення нормувальної енергії */
static float apply_hann_window(const float* input, float* output, size_t n) {
    float sum_sq_w = 0.0f;
    for (size_t i = 0; i < n; ++i) {
        float w = 0.5f * (1.0f - cosf(2.0f * M_PI_F * (float)i / (float)(n - 1)));
        output[i] = input[i] * w;
        sum_sq_w += w * w;
    }
    return sum_sq_w;
}

/* Обчислення дискретного перетворення Фур'є (DFT) для одного частотного відліку */
static void compute_dft_bin(const float* windowed_signal, size_t n, size_t k, float* re, float* im) {
    float sum_re = 0.0f;
    float sum_im = 0.0f;
    float angle_step = -2.0f * M_PI_F * (float)k / (float)n;

    for (size_t i = 0; i < n; ++i) {
        float angle = angle_step * (float)i;
        sum_re += windowed_signal[i] * cosf(angle);
        sum_im += windowed_signal[i] * sinf(angle);
    }
    *re = sum_re;
    *im = sum_im;
}

/* Пошук локального максимуму PSD у заданому частотному інтервалі */
static SchumannPeak find_peak_in_range(const float* psd, float f_start, float f_end, float fs, size_t n) {
    SchumannPeak result = {0.0f, 0.0f, 0.0f, false};
    size_t k_start = (size_t)lroundf((f_start * (float)n) / fs);
    size_t k_end   = (size_t)lroundf((f_end * (float)n) / fs);

    if (k_start >= n / 2 || k_end >= n / 2 || k_start >= k_end) {
        return result;
    }

    size_t max_k = k_start;
    float max_psd = psd[k_start];

    for (size_t k = k_start + 1; k <= k_end; ++k) {
        if (psd[k] > max_psd) {
            max_psd = psd[k];
            max_k = k;
        }
    }

    if (max_k > k_start && max_k < k_end) {
        /* Параболічна інтерполяція верхівки піку для підвищення точності */
        float alpha = psd[max_k - 1];
        float beta  = psd[max_k];
        float gamma = psd[max_k + 1];
        float delta = 0.5f * (alpha - gamma) / (alpha - 2.0f * beta + gamma);

        float exact_k = (float)max_k + delta;
        result.frequency_hz = (exact_k * fs) / (float)n;
        result.amplitude_psd = beta - 0.25f * (alpha - gamma) * delta;
        
        /* Приблизна оцінка добротності Q = f0 / delta_f (по рівню 0.5 від max) */
        float bandwidth_bins = 2.0f;
        if (beta > 1e-6f) {
            result.quality_factor = result.frequency_hz / ((bandwidth_bins * fs) / (float)n);
        }
        result.valid = true;
    }

    return result;
}

/* Головна функція аналізу масиву відліків */
bool schumann_analyze_buffer(const float* raw_samples, size_t n, SchumannReport* report) {
    if (!raw_samples || !report || n != SCHUMANN_N) {
        return false;
    }

    /* 1. Видалення DC зміщення */
    float dc_offset = 0.0f;
    for (size_t i = 0; i < n; ++i) {
        dc_offset += raw_samples[i];
    }
    dc_offset /= (float)n;

    float* zero_mean = (float*)malloc(n * sizeof(float));
    float* windowed  = (float*)malloc(n * sizeof(float));
    float* psd       = (float*)malloc((n / 2) * sizeof(float));

    if (!zero_mean || !windowed || !psd) {
        free(zero_mean);
        free(windowed);
        free(psd);
        return false;
    }

    for (size_t i = 0; i < n; ++i) {
        zero_mean[i] = raw_samples[i] - dc_offset;
    }

    /* 2. Застосування вікна Ганна */
    float sum_sq_w = apply_hann_window(zero_mean, windowed, n);

    /* 3. Обчислення спектральної густини потужності (PSD) для корисного діапазону 0-45 Гц */
    size_t k_max_schumann = (size_t)lroundf((45.0f * (float)n) / SCHUMANN_FS);
    float scale = 2.0f / (SCHUMANN_FS * sum_sq_w);

    for (size_t k = 0; k <= k_max_schumann; ++k) {
        float re, im;
        compute_dft_bin(windowed, n, k, &re, &im);
        psd[k] = scale * (re * re + im * im);
    }

    /* 4. Виділення піків перших трьох гармонік */
    report->peak_n1 = find_peak_in_range(psd, 6.0f,  10.0f, SCHUMANN_FS, n);
    report->peak_n2 = find_peak_in_range(psd, 12.0f, 16.0f, SCHUMANN_FS, n);
    report->peak_n3 = find_peak_in_range(psd, 18.0f, 24.0f, SCHUMANN_FS, n);

    free(zero_mean);
    free(windowed);
    free(psd);
    return true;
}
