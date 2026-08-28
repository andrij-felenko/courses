#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура для збереження повного набору параметрів антени */
typedef struct {
    double freq_mhz;        /* Робоча частота (МГц) */
    double lambda_mm;       /* Довжина хвилі у вакуумі (мм) */
    double diameter_mm;     /* Діаметр намотування спіралі D (мм) */
    double circumference_mm;/* Довжина кола витка C (мм) */
    double spacing_mm;      /* Крок витка S (мм) */
    double turn_length_mm;  /* Довжина провідника одного витка L0 (мм) */
    double total_length_mm; /* Загальна осьова довжина антени L (мм) */
    double wire_length_mm;  /* Загальна довжина дроту для N витків (мм) */
    double reflector_dim_mm;/* Мінімальний розмір екрана (мм) */
    double r_in_ohm;        /* Вхідний хвильовий опір антени (Ом) */
    double gain_dbi;        /* Коефіцієнт підсилення (дБі) */
    double hpbw_deg;        /* Ширина ДН за рівнем -3 дБ (градуси) */
    double z_match_ohm;     /* Опір 1/4-хвильового трансформатора до 50 Ом */
} HelixAntennaParams;

HelixAntennaParams calculate_helix(double freq_mhz, int num_turns) {
    HelixAntennaParams p;
    p.freq_mhz = freq_mhz;

    /* Швидкість світла c = 299 792.458 км/с */
    p.lambda_mm = 299792.458 / freq_mhz;

    /* Для центральної частоти обираємо довжину кола C = lambda */
    p.circumference_mm = p.lambda_mm;
    p.diameter_mm = p.circumference_mm / M_PI;

    /* Оптимальний кут нахилу alpha = 12.8 градусів (0.2234 радіана) */
    double alpha_rad = 12.8 * M_PI / 180.0;
    p.spacing_mm = p.circumference_mm * tan(alpha_rad);

    /* Довжина дроту одного витка L0 = sqrt(C^2 + S^2) */
    p.turn_length_mm = sqrt(p.circumference_mm * p.circumference_mm + 
                           p.spacing_mm * p.spacing_mm);

    p.total_length_mm = num_turns * p.spacing_mm;
    p.wire_length_mm = num_turns * p.turn_length_mm;

    /* Мінімальний діаметр/сторона рефлектора D_gp >= 0.75 * lambda */
    p.reflector_dim_mm = 0.75 * p.lambda_mm;

    /* Вхідний опір за формулою Крауса: R_in = 140 * (C / lambda) */
    double c_lambda = p.circumference_mm / p.lambda_mm;
    double s_lambda = p.spacing_mm / p.lambda_mm;
    p.r_in_ohm = 140.0 * c_lambda;

    /* Коефіцієнт підсилення: G = 12 * N * (C/lambda)^2 * (S/lambda) */
    double g_linear = 12.0 * num_turns * (c_lambda * c_lambda) * s_lambda;
    p.gain_dbi = 10.0 * log10(g_linear);

    /* Ширина діаграми спрямованості HPBW = 52 / ( (C/lambda) * sqrt(N * S/lambda) ) */
    p.hpbw_deg = 52.0 / (c_lambda * sqrt(num_turns * s_lambda));

    /* Опір чвертьхвильового трансформатора Z_t = sqrt(Z_in * Z_out) */
    p.z_match_ohm = sqrt(50.0 * p.r_in_ohm);

    return p;
}

int main(void) {
    double freq = 2437.0; /* Частота Wi-Fi / Bluetooth (МГц) */
    int turns = 8;        /* 8 витків */

    HelixAntennaParams h = calculate_helix(freq, turns);

    printf("=== Розрахунок спіральної антени (Краус) ===\n");
    printf("Частота:                  %.1f МГц (lambda = %.1f мм)\n", h.freq_mhz, h.lambda_mm);
    printf("Кількість витків N:        %d\n", turns);
    printf("Діаметр спіралі D:        %.2f мм\n", h.diameter_mm);
    printf("Крок витка S:             %.2f мм\n", h.spacing_mm);
    printf("Осьова довжина L:         %.1f мм\n", h.total_length_mm);
    printf("Загальна довжина дроту:   %.1f мм\n", h.wire_length_mm);
    printf("Розмір рефлектора D_gp:   >= %.1f мм\n", h.reflector_dim_mm);
    printf("-------------------------------------------\n");
    printf("Вхідний опір R_in:        %.1f Ом\n", h.r_in_ohm);
    printf("Трансформатор до 50 Ом:   Z0 = %.1f Ом (L = %.1f мм)\n", 
           h.z_match_ohm, h.lambda_mm / 4.0);
    printf("Коефіцієнт підсилення:     %.2f дБі\n", h.gain_dbi);
    printf("Ширина променя (HPBW):    %.1f градусів\n", h.hpbw_deg);

    return 0;
}
