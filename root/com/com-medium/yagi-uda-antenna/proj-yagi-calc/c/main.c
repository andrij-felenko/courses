#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    char name[32];
    double position_m;
    double length_m;
} YagiElement;

typedef struct {
    double frequency_mhz;
    double wavelength_m;
    double boom_length_m;
    int total_elements;
    YagiElement *elements;
} YagiAntenna;

YagiAntenna* yagi_calculate(double freq_mhz, int num_directors, double element_dia_mm) {
    if (freq_mhz <= 0.0 || num_directors < 1) {
        return NULL;
    }

    YagiAntenna *ant = (YagiAntenna*)malloc(sizeof(YagiAntenna));
    if (!ant) return NULL;

    ant->frequency_mhz = freq_mhz;
    ant->wavelength_m = 299.792458 / freq_mhz; // λ в метрах

    // Оцінка коефіцієнта укорочення k_v залежно від відношення d/λ
    double ratio = (element_dia_mm / 1000.0) / ant->wavelength_m;
    double k_v = 0.95 - 0.02 * log10(ratio > 1e-4 ? ratio : 1e-4);
    if (k_v > 0.98) k_v = 0.98;
    if (k_v < 0.91) k_v = 0.91;

    ant->total_elements = 2 + num_directors; // 1 Рефлектор + 1 Активний + N Директорів
    ant->elements = (YagiElement*)malloc(sizeof(YagiElement) * ant->total_elements);
    if (!ant->elements) {
        free(ant);
        return NULL;
    }

    double lambda = ant->wavelength_m;
    double current_z = 0.0;

    // 1. Рефлектор
    snprintf(ant->elements[0].name, sizeof(ant->elements[0].name), "Рефлектор");
    ant->elements[0].position_m = current_z;
    ant->elements[0].length_m = 0.485 * lambda * k_v;

    // 2. Активний диполь (відстань від рефлектора ~ 0.18 λ)
    current_z += 0.18 * lambda;
    snprintf(ant->elements[1].name, sizeof(ant->elements[1].name), "Активний диполь");
    ant->elements[1].position_m = current_z;
    ant->elements[1].length_m = 0.455 * lambda * k_v;

    // 3. Директори
    double dir_spacing = 0.15 * lambda;
    for (int i = 0; i < num_directors; i++) {
        current_z += dir_spacing;
        snprintf(ant->elements[2 + i].name, sizeof(ant->elements[2 + i].name), "Директор %d", i + 1);
        ant->elements[2 + i].position_m = current_z;

        // Коротшають за конусною залежністю
        double factor = 0.420 - 0.008 * i;
        if (factor < 0.370) factor = 0.370;
        ant->elements[2 + i].length_m = factor * lambda * k_v;

        // Пропорційне розширення відстані для далеких директорів
        dir_spacing = (0.15 + 0.01 * (i + 1)) * lambda;
        if (dir_spacing > 0.28 * lambda) dir_spacing = 0.28 * lambda;
    }

    ant->boom_length_m = current_z;
    return ant;
}

void yagi_free(YagiAntenna *ant) {
    if (ant) {
        if (ant->elements) free(ant->elements);
        free(ant);
    }
}

int main(void) {
    double freq = 433.92; // МГц (LPD/ISM діапазон)
    int directors = 4;
    double dia_mm = 6.0;   // 6 мм алюмінієва трубка

    YagiAntenna *ant = yagi_calculate(freq, directors, dia_mm);
    if (!ant) {
        fprintf(stderr, "Помилка обчислення параметрів антени\n");
        return 1;
    }

    printf("=========================================================\n");
    printf("  РОЗРАХУНОК АНТЕНИ ЯҐІ-УДА ДЛЯ ЧАСТОТИ %.2f МГц\n", ant->frequency_mhz);
    printf("  Довжина хвилі λ = %.4f м (%.1f см)\n", ant->wavelength_m, ant->wavelength_m * 100.0);
    printf("  Загальна довжина траверси (буму) = %.3f м\n", ant->boom_length_m);
    printf("=========================================================\n");
    printf("%-18s | %-16s | %-16s\n", "Елемент", "Позиція на бумі (мм)", "Довжина L (мм)");
    printf("---------------------------------------------------------\n");

    for (int i = 0; i < ant->total_elements; i++) {
        printf("%-18s | %18.1f | %14.1f\n",
               ant->elements[i].name,
               ant->elements[i].position_m * 1000.0,
               ant->elements[i].length_m * 1000.0);
    }
    printf("=========================================================\n");

    yagi_free(ant);
    return 0;
}
