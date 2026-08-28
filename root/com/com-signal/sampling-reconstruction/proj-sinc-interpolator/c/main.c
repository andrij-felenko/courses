#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура опису масиву дискретних відліків */
typedef struct {
    const double *data;
    size_t length;
    double sample_rate; /* Частота дискретизації fs (Гц) */
} signal_samples_t;

/* 1. Фіксатор нульового порядку (ZOH / Найближчий сусід) */
double interpolate_zoh(const signal_samples_t *sig, double t) {
    if (t < 0.0) return sig->data[0];
    
    double sample_index = t * sig->sample_rate;
    size_t idx = (size_t)floor(sample_index);
    
    if (idx >= sig->length) {
        return sig->data[sig->length - 1];
    }
    return sig->data[idx];
}

/* 2. Лінійна інтерполяція (FOH) */
double interpolate_linear(const signal_samples_t *sig, double t) {
    if (t <= 0.0) return sig->data[0];
    
    double sample_pos = t * sig->sample_rate;
    size_t idx0 = (size_t)floor(sample_pos);
    size_t idx1 = idx0 + 1;
    
    if (idx1 >= sig->length) {
        return sig->data[sig->length - 1];
    }
    
    double frac = sample_pos - (double)idx0;
    return (1.0 - frac) * sig->data[idx0] + frac * sig->data[idx1];
}

/* Нормована функція sinc(x) = sin(pi*x) / (pi*x) */
static inline double sinc(double x) {
    if (fabs(x) < 1e-9) return 1.0;
    double px = M_PI * x;
    return sin(px) / px;
}

/* Ядро Ланцоша радіуса a */
static inline double lanczos_kernel(double x, int a) {
    if (fabs(x) >= (double)a) return 0.0;
    return sinc(x) * sinc(x / (double)a);
}

/* 3. Віконна Sinc-інтерполяція Ланцоша радіуса a */
double interpolate_sinc_lanczos(const signal_samples_t *sig, double t, int radius) {
    double sample_pos = t * sig->sample_rate;
    long center_idx = (long)floor(sample_pos);
    
    double sum = 0.0;
    double weight_sum = 0.0;
    
    for (long i = center_idx - radius + 1; i <= center_idx + radius; i++) {
        if (i >= 0 && i < (long)sig->length) {
            double dx = sample_pos - (double)i;
            double w = lanczos_kernel(dx, radius);
            sum += sig->data[i] * w;
            weight_sum += w;
        }
    }
    
    /* Нормалізація суми ваг проти коливань постійної складової */
    return (weight_sum > 1e-9) ? (sum / weight_sum) : 0.0;
}

int main(void) {
    /* Синтез тестового сигналу: сума синусоїд 2 Гц та 5 Гц */
    const double fs = 20.0; /* Частота дискретизації 20 Гц */
    const size_t num_samples = 40;
    double samples[40];
    
    for (size_t i = 0; i < num_samples; i++) {
        double t = (double)i / fs;
        samples[i] = sin(2.0 * M_PI * 2.0 * t) + 0.5 * sin(2.0 * M_PI * 5.0 * t);
    }
    
    signal_samples_t sig = { .data = samples, .length = num_samples, .sample_rate = fs };
    
    printf("--- Тестування відновлення сигналу на C у точці t = 0.355 с ---
");
    double test_t = 0.355;
    double true_val = sin(2.0 * M_PI * 2.0 * test_t) + 0.5 * sin(2.0 * M_PI * 5.0 * test_t);
    
    double zoh_val = interpolate_zoh(&sig, test_t);
    double lin_val = interpolate_linear(&sig, test_t);
    double sinc_val = interpolate_sinc_lanczos(&sig, test_t, 4);
    
    printf("Справжнє значення:           %f
", true_val);
    printf("ZOH (ступінь):               %f (похибка: %.6f)
", zoh_val, fabs(zoh_val - true_val));
    printf("FOH (лінійна):               %f (похибка: %.6f)
", lin_val, fabs(lin_val - true_val));
    printf("Sinc-інтерполяція (Ланцош4): %f (похибка: %.6f)
", sinc_val, fabs(sinc_val - true_val));
    
    return 0;
}
