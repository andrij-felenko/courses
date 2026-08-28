#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define PI 3.14159265358979323846

/* Структура комплексного числа */
typedef struct {
    double r;
    double i;
} Complex;

/* Просте ітеративне швидке перетворення Фур'є (Cooley-Tukey Radix-2) */
static void fft_radix2(Complex *buf, size_t n) {
    /* Біт-реверсивне перевпорядкування */
    size_t j = 0;
    for (size_t i = 0; i < n - 1; ++i) {
        if (i < j) {
            Complex tmp = buf[i];
            buf[i] = buf[j];
            buf[j] = tmp;
        }
        size_t k = n >> 1;
        while (k <= j) {
            j -= k;
            k >>= 1;
        }
        j += k;
    }

    /* Метелики обчислення */
    for (size_t len = 2; len <= n; len <<= 1) {
        double ang = -2.0 * PI / (double)len;
        Complex wlen = { cos(ang), sin(ang) };
        for (size_t i = 0; i < n; i += len) {
            Complex w = { 1.0, 0.0 };
            for (size_t k = 0; k < len / 2; ++k) {
                Complex u = buf[i + k];
                Complex v = {
                    buf[i + k + len / 2].r * w.r - buf[i + k + len / 2].i * w.i,
                    buf[i + k + len / 2].r * w.i + buf[i + k + len / 2].i * w.r
                };
                buf[i + k].r = u.r + v.r;
                buf[i + k].i = u.i + v.i;
                buf[i + k + len / 2].r = u.r - v.r;
                buf[i + k + len / 2].i = u.i - v.i;

                double next_r = w.r * wlen.r - w.i * wlen.i;
                double next_i = w.r * wlen.i + w.i * wlen.r;
                w.r = next_r;
                w.i = next_i;
            }
        }
    }
}

/* Оцінка PSD за методом Велча */
static void compute_welch_psd(const Complex *samples, size_t num_samples,
                              size_t fft_size, double *psd_out) {
    for (size_t k = 0; k < fft_size; ++k) {
        psd_out[k] = 0.0;
    }

    /* Розрахунок вікна Ханна та його потужності */
    double *window = (double *)malloc(fft_size * sizeof(double));
    double win_energy = 0.0;
    for (size_t i = 0; i < fft_size; ++i) {
        window[i] = 0.5 * (1.0 - cos(2.0 * PI * (double)i / (double)(fft_size - 1)));
        win_energy += window[i] * window[i];
    }

    size_t hop_size = fft_size / 2; /* 50% перекриття */
    size_t num_frames = 0;
    Complex *fft_buf = (Complex *)malloc(fft_size * sizeof(Complex));

    for (size_t offset = 0; offset + fft_size <= num_samples; offset += hop_size) {
        for (size_t i = 0; i < fft_size; ++i) {
            fft_buf[i].r = samples[offset + i].r * window[i];
            fft_buf[i].i = samples[offset + i].i * window[i];
        }

        fft_radix2(fft_buf, fft_size);

        /* Спектральний зсув (FFT-shift) та підсумовування потужності */
        for (size_t i = 0; i < fft_size; ++i) {
            size_t shifted_idx = (i + fft_size / 2) % fft_size;
            double mag_sq = fft_buf[i].r * fft_buf[i].r + fft_buf[i].i * fft_buf[i].i;
            psd_out[shifted_idx] += mag_sq;
        }
        num_frames++;
    }

    if (num_frames > 0) {
        double norm = 1.0 / (num_frames * win_energy);
        for (size_t k = 0; k < fft_size; ++k) {
            psd_out[k] *= norm;
        }
    }

    free(window);
    free(fft_buf);
}

/* Інтегрування потужності у вказаній смузі частот */
static double integrate_power(const double *psd, size_t fft_size, double sample_rate,
                              double start_freq, double end_freq) {
    double df = sample_rate / (double)fft_size;
    double half_fs = sample_rate / 2.0;
    double power = 0.0;

    for (size_t k = 0; k < fft_size; ++k) {
        double freq = -half_fs + (double)k * df;
        if (freq >= start_freq && freq <= end_freq) {
            power += psd[k];
        }
    }
    return power;
}

/* Розрахунок ACLR та перевірка спектральної маски */
int main(void) {
    const double sample_rate = 61.44e6; /* 61.44 МГц дискретизація (3GPP 20 МГц) */
    const size_t fft_size = 2048;
    const size_t num_samples = 32768;
    const double ch_bw = 18.0e6;        /* Корисна смуга каналу 18 МГц (100 RB) */
    const double ch_spacing = 20.0e6;   /* Рознос каналів 20 МГц */

    Complex *iq_signal = (Complex *)malloc(num_samples * sizeof(Complex));

    /* Генерація тестового сигналу з нелінійним насиченням (кубічна інтермодуляція) */
    for (size_t n = 0; n < num_samples; ++n) {
        double t = (double)n / sample_rate;
        /* Базовий сигнал із кількома піднесучими */
        double i_lin = cos(2.0 * PI * 2.0e6 * t) + 0.8 * cos(2.0 * PI * 6.0e6 * t);
        double q_lin = sin(2.0 * PI * 2.0e6 * t) + 0.8 * sin(2.0 * PI * 6.0e6 * t);

        /* Моделювання нелінійності 3-го порядку підсилювача потужності (PA AM/AM) */
        double env_sq = i_lin * i_lin + q_lin * q_lin;
        double gain = 1.0 - 0.04 * env_sq; /* Нелінійне стиснення коефіцієнта підсилення */

        iq_signal[n].r = i_lin * gain;
        iq_signal[n].i = q_lin * gain;
    }

    double *psd = (double *)malloc(fft_size * sizeof(double));
    compute_welch_psd(iq_signal, num_samples, fft_size, psd);

    /* Інтегрування потужностей */
    double p_carrier = integrate_power(psd, fft_size, sample_rate, -ch_bw / 2.0, ch_bw / 2.0);
    double p_adj_lower = integrate_power(psd, fft_size, sample_rate,
                                         -ch_spacing - ch_bw / 2.0, -ch_spacing + ch_bw / 2.0);
    double p_adj_upper = integrate_power(psd, fft_size, sample_rate,
                                         ch_spacing - ch_bw / 2.0, ch_spacing + ch_bw / 2.0);

    double aclr_lower_db = 10.0 * log10(p_carrier / p_adj_lower);
    double aclr_upper_db = 10.0 * log10(p_carrier / p_adj_upper);

    printf("=== РЕЗУЛЬТАТИ СПЕКТРАЛЬНОГО АНАЛІЗУ (C) ===\n");
    printf("Потужність у головному каналі: %.4e Вт\n", p_carrier);
    printf("ACLR нижнього каналу (-20 МГц): %.2f дБ\n", aclr_lower_db);
    printf("ACLR верхнього каналу (+20 МГц): %.2f дБ\n", aclr_upper_db);

    bool pass_aclr = (aclr_lower_db >= 45.0) && (aclr_upper_db >= 45.0);
    printf("Норматив 3GPP ACLR (>= 45.0 дБ): %s\n", pass_aclr ? "ПРОЙДЕНО" : "НЕ ПРОЙДЕНО");

    free(iq_signal);
    free(psd);
    return pass_aclr ? 0 : 1;
}
