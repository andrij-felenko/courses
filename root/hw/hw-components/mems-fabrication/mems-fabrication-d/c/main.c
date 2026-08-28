#include <stdio.h>
#include <math.h>

typedef struct {
    double length_um;       /* Довжина балки, мкм */
    double thickness_um;    /* Товщина балки, мкм */
    double width_um;        /* Ширина балки, мкм */
    double target_depth_um; /* Цільова глибина травлення, мкм */
    double etch_rate_um_min;/* Швидкість травлення DRIE, мкм/хв */
    double cycle_time_s;    /* Час одного циклу Bosch, с */
} MemsParams;

void calculate_mems(const MemsParams* p) {
    const double E = 169e9;    /* Модуль Юнга кремнію, Па */
    const double rho = 2330.0; /* Густина кремнію, кг/м^3 */

    /* Переведення в метри */
    double L = p->length_um * 1e-6;
    double t = p->thickness_um * 1e-6;

    /* Розрахунок резонансної частоти */
    double f0 = 0.1615 * (t / (L * L)) * sqrt(E / rho);

    /* Розрахунок параметрів травлення */
    double total_time_min = p->target_depth_um / p->etch_rate_um_min;
    double total_time_s = total_time_min * 60.0;
    int num_cycles = (int)ceil(total_time_s / p->cycle_time_s);
    double depth_per_cycle_nm = (p->target_depth_um * 1000.0) / num_cycles;

    printf("Резонансна частота f0: %.2f кГц\n", f0 / 1000.0);
    printf("Загальний час травлення: %.2f хв\n", total_time_min);
    printf("Кількість циклів Bosch: %d\n", num_cycles);
    printf("Глибина за цикл: %.1f нм\n", depth_per_cycle_nm);
}

int main(void) {
    MemsParams params = {
        .length_um = 300.0,
        .thickness_um = 10.0,
        .width_um = 20.0,
        .target_depth_um = 50.0,
        .etch_rate_um_min = 4.5,
        .cycle_time_s = 3.5
    };
    calculate_mems(&params);
    return 0;
}
