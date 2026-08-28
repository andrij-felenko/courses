/* tdr_simulator.c — Калькулятор імпедансу та TDR-симулятор мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define EPSILON_0 8.854187817e-12
#define MU_0 (4.0 * PI * 1e-7)
#define C_SPEED 299792458.0

typedef struct {
    double z0;        /* Характеристичний імпеданс, Ом */
    double l0;        /* Погонна індуктивність, Гн/м */
    double c0;        /* Погонна ємність, Ф/м */
    double v_speed;   /* Швидкість хвилі в діелектрику, м/с */
    double delay_ps;  /* Затримка сигналу на 1 метр, пс/м */
} TLineParams;

/* Розрахунок коаксіального кабелю */
TLineParams calc_coaxial(double d_inner_mm, double d_outer_mm, double er) {
    TLineParams p;
    double ratio = d_outer_mm / d_inner_mm;
    p.l0 = (MU_0 / (2.0 * PI)) * log(ratio);
    p.c0 = (2.0 * PI * EPSILON_0 * er) / log(ratio);
    p.z0 = sqrt(p.l0 / p.c0);
    p.v_speed = C_SPEED / sqrt(er);
    p.delay_ps = (1.0 / p.v_speed) * 1e12;
    return p;
}

/* Розрахунок друкованої мікросмужки (Microstrip) */
TLineParams calc_microstrip(double width_mm, double height_mm, double thickness_mm, double er) {
    TLineParams p;
    /* Ефективна діелектрична проникність IPC */
    double e_eff = ((er + 1.0) / 2.0) + ((er - 1.0) / 2.0) * (1.0 / sqrt(1.0 + (12.0 * height_mm / width_mm)));
    p.z0 = (87.0 / sqrt(er + 1.41)) * log((5.98 * height_mm) / (0.8 * width_mm + thickness_mm));
    p.v_speed = C_SPEED / sqrt(e_eff);
    p.c0 = 1.0 / (p.z0 * p.v_speed);
    p.l0 = p.z0 / p.v_speed;
    p.delay_ps = (1.0 / p.v_speed) * 1e12;
    return p;
}

/* Симуляція рефлектограми TDR */
void simulate_tdr(const double* z_profile, size_t num_segments, double v_step) {
    printf("\n=== РЕЗУЛЬТАТИ TDR-СИМУЛЯЦІЇ (Вхідна напруга V_step = %.2f B) ===\n", v_step);
    printf("Сегмент | Імпеданс Z (Ом) | Коеф. відбиття Gamma | Напруга відгуку (В)\n");
    printf("----------------------------------------------------------------------\n");

    double v_forward = v_step;
    for (size_t i = 0; i < num_segments - 1; i++) {
        double z_curr = z_profile[i];
        double z_next = z_profile[i + 1];
        double gamma = (z_next - z_curr) / (z_next + z_curr);
        double v_reflected = v_forward * gamma;
        double v_measured = z_curr + v_reflected; /* Відгук на TDR */

        printf(" %2zu->%-2zu  |   %6.1f       |       %+.4f        |     %6.3f B\n",
               i, i + 1, z_next, gamma, v_measured);

        /* Оновлюємо пряму хвилю для наступного кроку з урахуванням пропускання */
        v_forward *= (1.0 + gamma);
    }
}

int main(void) {
    printf("--- Калькулятор імпедансу ліній передачі ---\n");

    /* 1. Коаксіал RG-58 (d = 0.9 мм, D = 2.95 мм, er = 2.25) */
    TLineParams coax = calc_coaxial(0.9, 2.95, 2.25);
    printf("Коаксіал RG-58: Z0 = %.1f Ом, L0 = %.2f нГн/м, C0 = %.2f пФ/м, v = %.2fe8 м/с, delay = %.0f пс/м\n",
           coax.z0, coax.l0 * 1e9, coax.c0 * 1e12, coax.v_speed / 1e8, coax.delay_ps);

    /* 2. Мікросмужка PCB 50 Ом (W = 0.35 мм, h = 0.20 мм, t = 0.035 мм, er = 4.2) */
    TLineParams mstrip = calc_microstrip(0.35, 0.20, 0.035, 4.2);
    printf("Мікросмужка PCB: Z0 = %.1f Ом, L0 = %.2f нГн/м, C0 = %.2f пФ/м, delay = %.0f пс/м\n",
           mstrip.z0, mstrip.l0 * 1e9, mstrip.c0 * 1e12, mstrip.delay_ps);

    /* 3. TDR-профіль доріжки з дефектами: 50 Ом -> 40 Ом (ємність роз'єму) -> 65 Ом (індуктивний вигин) -> обрив (1000 Ом) */
    double profile[] = {50.0, 40.0, 65.0, 1000.0};
    simulate_tdr(profile, 4, 1.0);

    return 0;
}
