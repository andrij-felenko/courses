#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* 
 * Автономна реалізація Radix-2 Cooley-Tukey FFT з двома напрямками (пряме / зворотне).
 * Вхідний масив buf переставляється за алгоритмом Bit-reversal.
 */
static void fft_radix2(double complex *buf, size_t n, int inverse) {
    if (n <= 1) return;

    /* 1. Перестановка бітів (Bit-reversal permutation) */
    size_t j = 0;
    for (size_t i = 0; i < n; i++) {
        if (i < j) {
            double complex tmp = buf[i];
            buf[i] = buf[j];
            buf[j] = tmp;
        }
        size_t m = n >> 1;
        while (m >= 1 && j >= m) {
            j -= m;
            m >>= 1;
        }
        j += m;
    }

    /* 2. Обчислення каскадів метеликів (Butterfly computation) */
    for (size_t len = 2; len <= n; len <<= 1) {
        double angle = (inverse ? 2.0 : -2.0) * M_PI / (double)len;
        double complex wlen = cexp(I * angle);

        for (size_t i = 0; i < n; i += len) {
            double complex w = 1.0 + 0.0 * I;
            for (size_t k = 0; k < len / 2; k++) {
                double complex u = buf[i + k];
                double complex v = buf[i + k + len / 2] * w;
                buf[i + k] = u + v;
                buf[i + k + len / 2] = u - v;
                w *= wlen;
            }
        }
    }

    /* 3. Нормування для зворотного IFFT */
    if (inverse) {
        for (size_t i = 0; i < n; i++) {
            buf[i] /= (double)n;
        }
    }
}

/* 
 * Головна функція обчислення аналітичного сигналу за алгоритмом Марпла в C.
 * Приймає дійснозначний вхідний масив input та повертає комплексний вихідний масив output.
 * Розмір n має бути степенем 2.
 */
int compute_analytic_signal_c(const double *input, double complex *output, size_t n) {
    if (!input || !output || n == 0 || (n & (n - 1)) != 0) {
        return -1; /* Помилка: неправильний розмір або NULL вказівник */
    }

    /* Копіювання дійснозначного сигналу в комплексний масив */
    for (size_t i = 0; i < n; i++) {
        output[i] = input[i] + 0.0 * I;
    }

    /* Крок 1: Пряме швидке перетворення Фур'є */
    fft_radix2(output, n, 0);

    /* Крок 2: Модифікація спектра за ваговим масивом H[k] */
    output[0] *= 1.0; /* Постійна складова (DC) */

    size_t half = n / 2;
    for (size_t k = 1; k < half; k++) {
        output[k] *= 2.0; /* Додатні частоти подвоюються */
    }

    output[half] *= 1.0; /* Частота Найквіста */

    for (size_t k = half + 1; k < n; k++) {
        output[k] = 0.0 + 0.0 * I; /* Від'ємні частоти обнуляються */
    }

    /* Крок 3: Зворотне швидке перетворення Фур'є (IFFT) */
    fft_radix2(output, n, 1);

    return 0;
}

int main(void) {
    const size_t N = 16;
    double signal[16];
    double complex analytic[16];

    /* Генерація тестового сигналу: cos(2*pi*2*i/N) */
    for (size_t i = 0; i < N; i++) {
        signal[i] = cos(2.0 * M_PI * 2.0 * (double)i / (double)N);
    }

    if (compute_analytic_signal_c(signal, analytic, N) == 0) {
        printf("Index \t Real (x) \t Imag (x_hat) \t Envelope (A)\n");
        printf("-----------------------------------------------------\n");
        for (size_t i = 0; i < N; i++) {
            double re = creal(analytic[i]);
            double im = cimag(analytic[i]);
            double env = cabs(analytic[i]);
            printf("%2zu \t %+.4f \t %+.4f \t %.4f\n", i, re, im, env);
        }
    }
    return 0;
}
