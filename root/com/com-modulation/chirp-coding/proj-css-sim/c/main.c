#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double real;
    double imag;
} Complex;

Complex complex_add(Complex a, Complex b) {
    Complex res = {a.real + b.real, a.imag + b.imag};
    return res;
}

Complex complex_mult(Complex a, Complex b) {
    Complex res = {
        a.real * b.real - a.imag * b.imag,
        a.real * b.imag + a.imag * b.real
    };
    return res;
}

double complex_abs(Complex a) {
    return sqrt(a.real * a.real + a.imag * a.imag);
}

void generate_gauss_noise(double *g1, double *g2) {
    double u1 = (double)rand() / (RAND_MAX + 1.0);
    double u2 = (double)rand() / (RAND_MAX + 1.0);
    if (u1 < 1e-10) u1 = 1e-10;
    double r = sqrt(-2.0 * log(u1));
    *g1 = r * cos(2.0 * M_PI * u2);
    *g2 = r * sin(2.0 * M_PI * u2);
}

int main(void) {
    srand((unsigned int)time(NULL));

    int SF = 7;
    int N = 1 << SF;
    int symbol_tx = 42;
    double snr_db = -10.0;

    Complex *s_tx = (Complex *)malloc(sizeof(Complex) * N);
    Complex *s_rx = (Complex *)malloc(sizeof(Complex) * N);
    Complex *down_chirp = (Complex *)malloc(sizeof(Complex) * N);
    Complex *dechirped = (Complex *)malloc(sizeof(Complex) * N);
    Complex *dft_out = (Complex *)malloc(sizeof(Complex) * N);

    if (!s_tx || !s_rx || !down_chirp || !dechirped || !dft_out) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    double snr_linear = pow(10.0, snr_db / 10.0);
    double noise_std = sqrt(1.0 / (2.0 * snr_linear));

    for (int n = 0; n < N; n++) {
        int idx = (n + symbol_tx) % N;
        double phase_tx = M_PI * ((double)(idx * idx)) / (double)N;
        s_tx[n].real = cos(phase_tx);
        s_tx[n].imag = sin(phase_tx);

        double n_real, n_imag;
        generate_gauss_noise(&n_real, &n_imag);
        s_rx[n].real = s_tx[n].real + n_real * noise_std;
        s_rx[n].imag = s_tx[n].imag + n_imag * noise_std;

        double phase_down = -M_PI * ((double)(n * n)) / (double)N;
        down_chirp[n].real = cos(phase_down);
        down_chirp[n].imag = sin(phase_down);
    }

    for (int n = 0; n < N; n++) {
        dechirped[n] = complex_mult(s_rx[n], down_chirp[n]);
    }

    for (int k = 0; k < N; k++) {
        dft_out[k].real = 0.0;
        dft_out[k].imag = 0.0;
        for (int n = 0; n < N; n++) {
            double angle = -2.0 * M_PI * k * n / (double)N;
            Complex exp_val = {cos(angle), sin(angle)};
            Complex term = complex_mult(dechirped[n], exp_val);
            dft_out[k] = complex_add(dft_out[k], term);
        }
    }

    int detected_symbol = 0;
    double max_mag = 0.0;
    for (int k = 0; k < N; k++) {
        double mag = complex_abs(dft_out[k]);
        if (mag > max_mag) {
            max_mag = mag;
            detected_symbol = k;
        }
    }

    printf("=== МОДЕЛЮВАННЯ LoRa CSS (Мова C) ===\n");
    printf("Spreading Factor (SF): %d (N = %d)\n", SF, N);
    printf("Переданий символ:      %d\n", symbol_tx);
    printf("Вхідний SNR:           %.1f dB\n", snr_db);
    printf("Декодований символ:    %d\n", detected_symbol);
    printf("Пікова амплітуда FFT:  %.2f\n", max_mag);

    if (detected_symbol == symbol_tx) {
        printf("РЕЗУЛЬТАТ: УСПІШНЕ ДЕКОДУВАННЯ ПІД ШУМОМ!\n");
    } else {
        printf("РЕЗУЛЬТАТ: ПОМИЛКА ДЕКОДУВАННЯ\n");
    }

    free(s_tx);
    free(s_rx);
    free(down_chirp);
    free(dechirped);
    free(dft_out);

    return 0;
}
