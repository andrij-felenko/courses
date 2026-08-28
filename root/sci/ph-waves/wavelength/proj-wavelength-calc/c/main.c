#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define SPEED_OF_LIGHT_VACUUM 299792458.0

typedef struct {
    double frequency_hz;
    double speed_m_s;
    double wavelength_m;
    double wavenumber_k;
    double period_s;
} WaveProperties;

/* Обчислення швидкості звуку у сухому повітрі (°C) */
double acoustic_speed_in_air(double temp_celsius) {
    return 331.3 * sqrt(1.0 + temp_celsius / 273.15);
}

/* Обчислення параметрів хвилі з валідацією вхідних даних */
int calculate_wave_properties(double frequency_hz, double speed_m_s, WaveProperties* out_prop) {
    if (frequency_hz <= 0.0 || speed_m_s <= 0.0 || !out_prop) {
        return 0;
    }
    out_prop->frequency_hz = frequency_hz;
    out_prop->speed_m_s = speed_m_s;
    out_prop->wavelength_m = speed_m_s / frequency_hz;
    out_prop->wavenumber_k = (2.0 * M_PI) / out_prop->wavelength_m;
    out_prop->period_s = 1.0 / frequency_hz;
    return 1;
}

/* Розрахунок вузлів стоячої хвилі у статичний масив */
int calculate_standing_wave_nodes(double length_m, double wavelength_m, double* out_nodes, size_t max_nodes) {
    if (wavelength_m <= 0.0 || length_m < 0.0 || !out_nodes) {
        return 0;
    }
    double spacing = wavelength_m / 2.0;
    size_t count = 0;
    for (double pos = 0.0; pos <= length_m + 1e-9 && count < max_nodes; pos += spacing) {
        out_nodes[count++] = pos;
    }
    return (int)count;
}

int main(void) {
    WaveProperties prop;
    double v_air = acoustic_speed_in_air(20.0);
    
    if (calculate_wave_properties(40000.0, v_air, &prop)) {
        printf("=== 1. Акустика (40 кГц у повітрі 20°C) ===\n");
        printf("Швидкість: %.2f м/с\n", prop.speed_m_s);
        printf("Довжина хвилі: %.3f мм\n", prop.wavelength_m * 1000.0);
        printf("Хвильове число k: %.2f рад/м\n", prop.wavenumber_k);
    }

    double em_speed = SPEED_OF_LIGHT_VACUUM / 1.444; // кварцове волокно n = 1.444
    if (calculate_wave_properties(193.4e12, em_speed, &prop)) {
        printf("\n=== 2. Волоконна оптика (193.4 ТГц) ===\n");
        printf("Швидкість у волокні: %.4e м/с\n", prop.speed_m_s);
        printf("Довжина хвилі: %.2f нм\n", prop.wavelength_m * 1e9);
        printf("Хвильове число k: %.4e рад/м\n", prop.wavenumber_k);
    }

    double nodes[16];
    double lambda_500 = v_air / 500.0;
    int node_count = calculate_standing_wave_nodes(1.0, lambda_500, nodes, 16);
    printf("\n=== 3. Вузли стоячої хвилі (500 Гц, L = 1.0 м) ===\n");
    for (int i = 0; i < node_count; ++i) {
        printf("Вузол %d: %.3f м\n", i + 1, nodes[i]);
    }

    return 0;
}
