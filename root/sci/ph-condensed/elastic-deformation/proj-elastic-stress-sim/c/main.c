#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    const char* name;
    double length;          /* L (м) */
    double diameter;        /* d (м) */
    double young_modulus;   /* E (Па) */
    double poisson_ratio;   /* ν */
    double alpha;           /* α (1/K) */
    double delta_t;         /* ΔT (K) */
} Segment;

typedef struct {
    double stress_MPa;
    double strain_mech_pct;
    double delta_l_mm;
    double delta_d_um;
    double energy_J;
} SegmentResult;

void calculate_segment(const Segment* seg, double force, SegmentResult* res) {
    double area = M_PI * seg->diameter * seg->diameter / 4.0;
    double stress = force / area;
    double strain_mech = stress / seg->young_modulus;
    double strain_therm = seg->alpha * seg->delta_t;
    double strain_total = strain_mech + strain_therm;

    double delta_l = seg->length * strain_total;
    double delta_d = -seg->poisson_ratio * strain_mech * seg->diameter;
    double volume = area * seg->length;
    double energy = 0.5 * stress * strain_mech * volume;

    res->stress_MPa = stress / 1e6;
    res->strain_mech_pct = strain_mech * 100.0;
    res->delta_l_mm = delta_l * 1000.0;
    res->delta_d_um = delta_d * 1e6;
    res->energy_J = energy;
}

int main(void) {
    Segment rod[] = {
        {"Сталевий сегмент", 0.5, 0.02, 210e9, 0.30, 0.0, 0.0},
        {"Алюмінієвий сегмент", 0.3, 0.025, 70e9, 0.33, 0.0, 0.0}
    };
    size_t count = sizeof(rod) / sizeof(rod[0]);
    double force = 50000.0; /* 50 кН */

    double total_delta_l_mm = 0.0;
    double total_energy_J = 0.0;

    printf("=== Результати розрахунку (C) ===\n");
    for (size_t i = 0; i < count; ++i) {
        SegmentResult res;
        calculate_segment(&rod[i], force, &res);

        printf("[%s]\n", rod[i].name);
        printf("  Напруження σ:       %.2f МПа\n", res.stress_MPa);
        printf("  Пружна деформація: %.4f %%\n", res.strain_mech_pct);
        printf("  Подовження ΔL:      %.4f мм\n", res.delta_l_mm);
        printf("  Зміна діаметра Δd: %.2f мкм\n", res.delta_d_um);
        printf("  Енергія U:          %.4f Дж\n", res.energy_J);

        total_delta_l_mm += res.delta_l_mm;
        total_energy_J += res.energy_J;
    }

    printf("Загальне подовження стержня: %.4f мм\n", total_delta_l_mm);
    printf("Повна потенціальна енергія:   %.4f Дж\n", total_energy_J);

    return 0;
}
