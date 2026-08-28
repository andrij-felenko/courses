#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define M_PI_F 3.14159265358979323846f

typedef struct {
    float real;
    float imag;
} Complex;

typedef struct {
    float freq_hz;
    float amplitude;
    const char *classification;
} SpectralPeak;

// Бітова перестановка для ШПФ за основою 2 (Cooley-Tukey In-Place)
static void bit_reverse(Complex *x, size_t n) {
    size_t j = 0;
    for (size_t i = 0; i < n - 1; i++) {
        if (i < j) {
            Complex temp = x[i];
            x[i] = x[j];
            x[j] = temp;
        }
        size_t k = n / 2;
        while (k <= j) {
            j -= k;
            k /= 2;
        }
        j += k;
    }
}

// Радікс-2 Швидке перетворення Фур'є
void fft(Complex *x, size_t n) {
    bit_reverse(x, n);

    for (size_t len = 2; len <= n; len <<= 1) {
        float angle = -2.0f * M_PI_F / (float)len;
        Complex wlen = { .real = cosf(angle), .imag = sinf(angle) };

        for (size_t i = 0; i < n; i += len) {
            Complex w = { .real = 1.0f, .imag = 0.0f };
            for (size_t j = 0; j < len / 2; j++) {
                Complex u = x[i + j];
                Complex v = {
                    .real = x[i + j + len / 2].real * w.real - x[i + j + len / 2].imag * w.imag,
                    .imag = x[i + j + len / 2].real * w.imag + x[i + j + len / 2].imag * w.real
                };
                x[i + j].real = u.real + v.real;
                x[i + j].imag = u.imag + v.imag;
                x[i + j + len / 2].real = u.real - v.real;
                x[i + j + len / 2].imag = u.imag - v.imag;

                float next_w_real = w.real * wlen.real - w.imag * wlen.imag;
                w.imag = w.real * wlen.imag + w.imag * wlen.real;
                w.real = next_w_real;
            }
        }
    }
}

// Конвеєр спектрального аналізу вібрацій
void analyze_vibrations(const float *raw_samples, size_t n, float sample_rate, 
                        float expected_rpm, int num_blades) {
    if ((n & (n - 1)) != 0 || n == 0) {
        printf("Помилка: розмір вибірки повинен бути степенем двійки!\n");
        return;
    }

    Complex *buf = (Complex *)malloc(n * sizeof(Complex));
    if (!buf) return;

    // 1. Зняття постійного зсуву (DC offset)
    float mean = 0.0f;
    for (size_t i = 0; i < n; i++) mean += raw_samples[i];
    mean /= (float)n;

    // 2. Накладання вікна Ганна (Hann Window)
    for (size_t i = 0; i < n; i++) {
        float window = 0.5f * (1.0f - cosf(2.0f * M_PI_F * (float)i / (float)(n - 1)));
        buf[i].real = (raw_samples[i] - mean) * window;
        buf[i].imag = 0.0f;
    }

    // 3. Обчислення ШПФ
    fft(buf, n);

    // 4. Розрахунок амплітудного спектра та загального RMS
    size_t num_bins = n / 2;
    float *magnitudes = (float *)malloc(num_bins * sizeof(float));
    float df = sample_rate / (float)n;
    float total_energy = 0.0f;

    for (size_t i = 0; i < num_bins; i++) {
        float mag = sqrtf(buf[i].real * buf[i].real + buf[i].imag * buf[i].imag);
        // Масштабування: врахування відсіченої від'ємної половини та вікна Ганна (множник 4/N)
        magnitudes[i] = (mag * 4.0f) / (float)n;
        total_energy += magnitudes[i] * magnitudes[i];
    }
    float total_rms = sqrtf(total_energy * 0.5f);

    // 5. Пошук двох найсильніших спектральних піків
    float max1 = 0.0f, max2 = 0.0f;
    size_t bin1 = 0, bin2 = 0;

    for (size_t i = 1; i < num_bins - 1; i++) {
        if (magnitudes[i] > magnitudes[i - 1] && magnitudes[i] > magnitudes[i + 1]) {
            if (magnitudes[i] > max1) {
                max2 = max1; bin2 = bin1;
                max1 = magnitudes[i]; bin1 = i;
            } else if (magnitudes[i] > max2) {
                max2 = magnitudes[i]; bin2 = i;
            }
        }
    }

    float motor_freq_hz = expected_rpm / 60.0f;
    float bpf_freq_hz = motor_freq_hz * (float)num_blades;

    printf("=== ЗВІТ СПЕКТРАЛЬНОГО АНАЛІЗУ BLACKBOX ===\n");
    printf("Частота дискретизації:   %6.1f Гц (Крок біна: %4.2f Гц)\n", sample_rate, df);
    printf("Очікувана частота мотора: %6.1f Гц (1x RPM при %.0f об/хв)\n", motor_freq_hz, expected_rpm);
    printf("Лопатева частота (BPF):  %6.1f Гц (%d лопаті)\n", bpf_freq_hz, num_blades);
    printf("Загальний RMS вібрацій:  %6.2f град/с (або м/с^2)\n\n", total_rms);

    printf("Знайдені домінантні піки:\n");
    size_t detected_bins[2] = { bin1, bin2 };
    for (int k = 0; k < 2; k++) {
        size_t b = detected_bins[k];
        if (b == 0) continue;
        float freq = (float)b * df;
        float amp = magnitudes[b];
        const char *diag = "Невідомий структурний резонанс";

        if (fabsf(freq - motor_freq_hz) < 2.0f * df || fabsf(freq - motor_freq_hz) / motor_freq_hz < 0.05f) {
            diag = "1x RPM: Статичний/динамічний дисбаланс ротора";
        } else if (fabsf(freq - bpf_freq_hz) < 2.0f * df || fabsf(freq - bpf_freq_hz) / bpf_freq_hz < 0.05f) {
            diag = "BPF: Аеродинамічна взаємодія / дефект лопатей";
        }

        printf("  Пік %d: %6.1f Гц | Амплітуда: %5.2f | Джерело: %s\n", k + 1, freq, amp, diag);
    }

    free(buf);
    free(magnitudes);
}

int main(void) {
    const size_t n = 1024;
    const float fs = 2000.0f;       // Логування Blackbox на 2 кГц
    const float rpm = 15000.0f;     // Мотор на 15 000 об/хв (250 Гц)
    const int blades = 3;           // Трилопатевий пропелер (BPF = 750 Гц)
    float samples[1024];

    // Синтез тестового сигналу з шумом і піками (250 Гц дисбаланс, 750 Гц BPF, 410 Гц резонанс рами)
    for (size_t i = 0; i < n; i++) {
        float t = (float)i / fs;
        samples[i] = 8.5f * sinf(2.0f * M_PI_F * 250.0f * t)   // 1x RPM
                   + 3.2f * sinf(2.0f * M_PI_F * 750.0f * t)   // BPF
                   + 5.0f * sinf(2.0f * M_PI_F * 410.0f * t)   // Резонанс рами
                   + ((float)rand() / (float)RAND_MAX - 0.5f) * 1.5f; // Білий шум
    }

    analyze_vibrations(samples, n, fs, rpm, blades);
    return 0;
}
