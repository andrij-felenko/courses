/* C Implementation: White Noise Generation & Welch PSD Estimation */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Standard Box-Muller transform for Gaussian white noise generation */
double generate_gaussian_sample(double std_dev) {
    double u1 = (double)rand() / RAND_MAX;
    double u2 = (double)rand() / RAND_MAX;
    if (u1 < 1e-12) u1 = 1e-12; /* Protection against log(0) */
    double z0 = sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
    return z0 * std_dev;
}

/* Radix-2 Cooley-Tukey In-Place Fast Fourier Transform */
void fft_radix2(double complex *x, int N) {
    if (N <= 1) return;
    
    /* Bit-reversal permutation */
    int j = 0;
    for (int i = 0; i < N; i++) {
        if (i < j) {
            double complex temp = x[i];
            x[i] = x[j];
            x[j] = temp;
        }
        int m = N >> 1;
        while (m >= 1 && j >= m) {
            j -= m;
            m >>= 1;
        }
        j += m;
    }
    
    /* Iterative Butterfly computation */
    for (int len = 2; len <= N; len <<= 1) {
        double ang = -2.0 * M_PI / len;
        double complex wlen = cos(ang) + I * sin(ang);
        for (int i = 0; i < N; i += len) {
            double complex w = 1.0;
            for (int k = 0; k < len / 2; k++) {
                double complex u = x[i + k];
                double complex v = x[i + k + len / 2] * w;
                x[i + k] = u + v;
                x[i + k + len / 2] = u - v;
                w *= wlen;
            }
        }
    }
}

/* Welch Power Spectral Density Estimation Algorithm */
void compute_welch_psd(const double *signal, int total_samples, int segment_len,
                       double fs, double *psd_out) {
    int num_bins = segment_len / 2 + 1;
    for (int i = 0; i < num_bins; i++) psd_out[i] = 0.0;

    int step = segment_len / 2; /* 50% Overlap */
    int num_segments = (total_samples - segment_len) / step + 1;

    /* Prepare Hann Window and calculate window power sum S_w */
    double *window = (double *)malloc(segment_len * sizeof(double));
    double win_sum_sq = 0.0;
    for (int n = 0; n < segment_len; n++) {
        window[n] = 0.5 * (1.0 - cos(2.0 * M_PI * n / (segment_len - 1)));
        win_sum_sq += window[n] * window[n];
    }

    double complex *buffer = (double complex *)malloc(segment_len * sizeof(double complex));

    for (int seg = 0; seg < num_segments; seg++) {
        int offset = seg * step;
        for (int n = 0; n < segment_len; n++) {
            buffer[n] = signal[offset + n] * window[n];
        }

        fft_radix2(buffer, segment_len);

        /* One-sided PSD accumulation with ENBW scaling */
        for (int k = 0; k < num_bins; k++) {
            double mag_sq = cabs(buffer[k]) * cabs(buffer[k]);
            double scale = (k == 0 || k == segment_len / 2) ? 1.0 : 2.0;
            psd_out[k] += scale * mag_sq / (fs * win_sum_sq);
        }
    }

    /* Averaging over all segments */
    for (int k = 0; k < num_bins; k++) {
        psd_out[k] /= num_segments;
    }

    free(window);
    free(buffer);
}

int main(void) {
    double fs = 10000.0;          /* Sampling rate: 10 kHz */
    double G0_target = 1e-4;       /* Target PSD: 1e-4 V^2/Hz */
    double duration = 2.0;         /* Signal duration: 2 seconds */
    int N = (int)(fs * duration);
    int seg_len = 1024;

    /* Correct discrete std_dev scaling for Gaussian noise generator */
    double std_dev = sqrt(G0_target * (fs / 2.0));

    double *signal = (double *)malloc(N * sizeof(double));
    for (int i = 0; i < N; i++) {
        signal[i] = generate_gaussian_sample(std_dev);
    }

    int num_bins = seg_len / 2 + 1;
    double *psd = (double *)malloc(num_bins * sizeof(double));

    compute_welch_psd(signal, N, seg_len, fs, psd);

    printf("Welch PSD Estimation Results (Target G0 = %.6f V^2/Hz):\n", G0_target);
    printf("Freq (Hz)\tPSD (V^2/Hz)\n");
    for (int k = 0; k <= 5; k++) {
        double freq = k * (fs / seg_len);
        printf("%.2f\t\t%.6f\n", freq, psd[k]);
    }

    free(signal);
    free(psd);
    return 0;
}
