#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double base_length_m;      /* Базова відстань L (м) */
    int num_teeth;             /* Кількість зубців N */
    double speed_of_light;     /* Істинна швидкість світла c (м/с) */
} FizeauSetup;

/* Обчислення коефіцієнта пропускання зубчастого колеса у момент часу t */
static double fizeau_gate_transmission(double t, double freq_hz, int num_teeth) {
    double period = 1.0 / (num_teeth * freq_hz);
    double phase = fmod(t, period);
    if (phase < 0.0) phase += period;
    /* 50% часу відкритий проміжок, 50% — закритий зубцем */
    return (phase < (period / 2.0)) ? 1.0 : 0.0;
}

/* Обчислення середньої інтенсивності на окулярі методом чисельного інтегрування */
double calculate_fizeau_intensity(const FizeauSetup *setup, double freq_hz, int samples) {
    double t_flight = 2.0 * setup->base_length_m / setup->speed_of_light;
    double period = 1.0 / (setup->num_teeth * freq_hz);
    double dt = period / samples;
    double sum_intensity = 0.0;

    for (int i = 0; i < samples; ++i) {
        double t_emit = i * dt;
        double t_recv = t_emit + t_flight;
        double t_in = fizeau_gate_transmission(t_emit, freq_hz, setup->num_teeth);
        double t_out = fizeau_gate_transmission(t_recv, freq_hz, setup->num_teeth);
        sum_intensity += (t_in * t_out);
    }

    return sum_intensity / samples;
}

int main(void) {
    FizeauSetup setup = { 8633.0, 720, 299792458.0 };
    double freq_start = 1.0;
    double freq_end = 25.0;
    double step = 0.1;

    printf("=== Симуляція експерименту Фізо (L = %.1f м, N = %d) ===\n", setup.base_length_m, setup.num_teeth);
    printf("Частота (Гц) | Відносна інтенсивність | Оцінка c (км/с)\n");
    printf("-----------------------------------------------------\n");

    double min_intensity = 1.0;
    double min_freq = 0.0;

    for (double f = freq_start; f <= freq_end; f += step) {
        double intensity = calculate_fizeau_intensity(&setup, f, 1000);
        if (intensity < min_intensity) {
            min_intensity = intensity;
            min_freq = f;
        }
        if (fmod(f, 2.0) < step) {
            double c_calc = 4.0 * setup.num_teeth * setup.base_length_m * f / 1000.0;
            printf("%11.2f | %22.4f | %14.2f\n", f, intensity, c_calc);
        }
    }

    double c_est = 4.0 * setup.num_teeth * setup.base_length_m * min_freq / 1000.0;
    printf("-----------------------------------------------------\n");
    printf("Перше затемнення зафіксовано при f = %.2f Гц\n", min_freq);
    printf("Обчислена швидкість світла: %.2f км/с\n", c_est);

    return 0;
}
