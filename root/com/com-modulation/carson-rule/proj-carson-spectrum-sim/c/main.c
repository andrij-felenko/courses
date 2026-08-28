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

/* Проста реалізація БПФ Кулі-Тьюкі (Cooley-Tukey FFT) з проріджуванням за часом */
static void fft(Complex *x, size_t n) {
    if (n <= 1) return;

    Complex *even = (Complex *)malloc((n / 2) * sizeof(Complex));
    Complex *odd  = (Complex *)malloc((n / 2) * sizeof(Complex));

    for (size_t i = 0; i < n / 2; ++i) {
        even[i] = x[2 * i];
        odd[i]  = x[2 * i + 1];
    }

    fft(even, n / 2);
    fft(odd,  n / 2);

    for (size_t k = 0; k < n / 2; ++k) {
        double angle = -2.0 * M_PI * (double)k / (double)n;
        Complex t;
        t.real = cos(angle) * odd[k].real - sin(angle) * odd[k].imag;
        t.imag = cos(angle) * odd[k].imag + sin(angle) * odd[k].real;

        x[k].real           = even[k].real + t.real;
        x[k].imag           = even[k].imag + t.imag;
        x[k + n / 2].real   = even[k].real - t.real;
        x[k + n / 2].imag   = even[k].imag - t.imag;
    }

    free(even);
    free(odd);
}

typedef struct {
    double beta;
    double carson_bandwidth_hz;
    double carson_power_ratio;
    size_t harmonic_count_carson;
    size_t harmonic_count_98pct;
    size_t harmonic_count_99pct;
} FmSpectrumResult;

FmSpectrumResult analyze_fm_spectrum(double carrier_freq, double mod_freq, double dev_freq, size_t fft_size) {
    FmSpectrumResult res;
    res.beta = dev_freq / mod_freq;
    res.carson_bandwidth_hz = 2.0 * (dev_freq + mod_freq);
    res.harmonic_count_carson = (size_t)floor(res.beta + 1.0);

    double fs = carrier_freq * 8.0; /* Частота дискретизації перевищує несучу у 8 разів */
    Complex *signal = (Complex *)malloc(fft_size * sizeof(Complex));

    /* Генеруємо ЧМ-сигнал з згладжувальним вікном Ханна */
    for (size_t i = 0; i < fft_size; ++i) {
        double t = (double)i / fs;
        double phase = 2.0 * M_PI * carrier_freq * t + res.beta * sin(2.0 * M_PI * mod_freq * t);
        double window = 0.5 * (1.0 - cos(2.0 * M_PI * (double)i / (double)(fft_size - 1)));
        
        signal[i].real = cos(phase) * window;
        signal[i].imag = 0.0;
    }

    fft(signal, fft_size);

    /* Обчислюємо спектральну потужність кожної гармоніки */
    double *power = (double *)calloc(fft_size / 2, sizeof(double));
    double total_power = 0.0;

    for (size_t i = 0; i < fft_size / 2; ++i) {
        double mag = sqrt(signal[i].real * signal[i].real + signal[i].imag * signal[i].imag);
        power[i] = mag * mag;
        total_power += power[i];
    }

    /* Визначаємо енергію в бічних гармоніках */
    double bin_resolution = fs / (double)fft_size;
    size_t carrier_bin = (size_t)round(carrier_freq / bin_resolution);
    size_t mod_bin_step = (size_t)round(mod_freq / bin_resolution);

    double carson_power = power[carrier_bin];
    for (size_t n = 1; n <= res.harmonic_count_carson; ++n) {
        if (carrier_bin >= n * mod_bin_step) {
            carson_power += power[carrier_bin - n * mod_bin_step];
        }
        if (carrier_bin + n * mod_bin_step < fft_size / 2) {
            carson_power += power[carrier_bin + n * mod_bin_step];
        }
    }

    res.carson_power_ratio = carson_power / total_power;

    /* Шукаємо номери гармонік для 98% та 99% енергії */
    double accum_power = power[carrier_bin];
    size_t n = 1;
    res.harmonic_count_98pct = 0;
    res.harmonic_count_99pct = 0;

    while (n < fft_size / 4) {
        if (carrier_bin >= n * mod_bin_step) {
            accum_power += power[carrier_bin - n * mod_bin_step];
        }
        if (carrier_bin + n * mod_bin_step < fft_size / 2) {
            accum_power += power[carrier_bin + n * mod_bin_step];
        }

        double ratio = accum_power / total_power;
        if (ratio >= 0.98 && res.harmonic_count_98pct == 0) {
            res.harmonic_count_98pct = n;
        }
        if (ratio >= 0.99 && res.harmonic_count_99pct == 0) {
            res.harmonic_count_99pct = n;
            break;
        }
        n++;
    }

    free(signal);
    free(power);
    return res;
}

int main(void) {
    double mod_freq = 15000.0; /* Модулюючий тон 15 кГц */
    double devs[] = { 7500.0, 15000.0, 36072.0, 75000.0, 150000.0 };
    size_t dev_count = sizeof(devs) / sizeof(devs[0]);

    printf("=== Аналіз спектра ЧМ за правилом Карсона (C) ===\n\n");
    printf("%-8s | %-8s | %-12s | %-12s | %-10s | %-10s\n",
           "β", "Δf (кГц)", "B_Carson", "Потужність", "N_Carson", "N_98%");
    printf("------------------------------------------------------------------------\n");

    for (size_t i = 0; i < dev_count; ++i) {
        double dev = devs[i];
        FmSpectrumResult r = analyze_fm_spectrum(1000000.0, mod_freq, dev, 8192);
        printf("%-8.2f | %-8.1f | %-10.1f кГц | %-10.2f%% | %-10zu | %-10zu\n",
               r.beta, dev / 1000.0, r.carson_bandwidth_hz / 1000.0,
               r.carson_power_ratio * 100.0, r.harmonic_count_carson, r.harmonic_count_98pct);
    }

    return 0;
}
