#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double mod_freq_hz;         /* Модуляційна частота f_m (Гц) */
    double true_distance_m;     /* Справжня відстань L (м) */
    double speed_of_light;     /* Константа c (м/с) */
} PhaseLidar;

/* Обчислення різниці фаз методом квадратурної демодуляції (IQ) */
double extract_phase_shift(const double *ref_signal, const double *meas_signal, int num_samples) {
    double I_comp = 0.0;
    double Q_comp = 0.0;

    for (int i = 0; i < num_samples; ++i) {
        I_comp += meas_signal[i] * ref_signal[i];
        Q_comp += meas_signal[i] * sin(2.0 * M_PI * i / num_samples);
    }

    return atan2(Q_comp, I_comp);
}

int main(void) {
    PhaseLidar lidar = { 50000000.0, 15.45, 299792458.0 }; /* f_m = 50 МГц, L = 15.45 м */
    int samples = 1000;
    double ref[1000];
    double meas[1000];

    double t_flight = 2.0 * lidar.true_distance_m / lidar.speed_of_light;
    double phase_shift_true = 2.0 * M_PI * lidar.mod_freq_hz * t_flight;

    /* Генерація тестових дискретизованих сигналів */
    for (int i = 0; i < samples; ++i) {
        double t = (double)i / (samples * lidar.mod_freq_hz);
        ref[i] = cos(2.0 * M_PI * lidar.mod_freq_hz * t);
        meas[i] = cos(2.0 * M_PI * lidar.mod_freq_hz * t - phase_shift_true);
    }

    double delta_phi = extract_phase_shift(ref, meas, samples);
    if (delta_phi < 0.0) delta_phi += 2.0 * M_PI;

    double dist_est = (lidar.speed_of_light * delta_phi) / (4.0 * M_PI * lidar.mod_freq_hz);

    printf("=== Демодуляція фазового сигналу LiDAR ===\n");
    printf("Істинна відстань: %.4f м\n", lidar.true_distance_m);
    printf("Виміряний фазовий зсув: %.4f рад (%.2f градусів)\n", delta_phi, delta_phi * 180.0 / M_PI);
    printf("Обчислена відстань: %.4f м\n", dist_est);
    printf("Похибка вимірювання: %.2f мм\n", fabs(dist_est - lidar.true_distance_m) * 1000.0);

    return 0;
}
