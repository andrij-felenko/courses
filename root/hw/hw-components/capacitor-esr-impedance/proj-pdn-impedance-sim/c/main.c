#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура опису групи однакових конденсаторів */
typedef struct {
    const char *name;      /* Назва/технологія компонента */
    double c_farad;        /* Ефективна ємність (Ф) */
    double esr_ohm;        /* ESR компонента (Ом) */
    double esl_henry;      /* Власний ESL корпусу (Гн) */
    double l_via_henry;    /* Індуктивність монтажних отворів (Гн) */
    double r_trace_ohm;    /* Опір траси підключення (Ом) */
    int count;             /* Кількість увімкнених паралельно штук */
} CapGroup;

/* Результат розрахунку в одній частотній точці */
typedef struct {
    double freq_hz;
    double z_mag_ohm;
    double phase_deg;
    bool exceeds_target;
} FreqPoint;

/* Обчислення комплексного імпедансу однієї гілки */
static double complex calc_branch_z(const CapGroup *grp, double omega) {
    double r_tot = grp->esr_ohm + grp->r_trace_ohm;
    double l_tot = grp->esl_henry + grp->l_via_henry;
    double x_react = omega * l_tot - 1.0 / (omega * grp->c_farad);
    return r_tot + x_react * I;
}

/* Розрахунок сумарного імпедансу PDN на частоті freq_hz */
static double complex calc_pdn_z(const CapGroup *groups, int num_groups, double freq_hz) {
    double omega = 2.0 * M_PI * freq_hz;
    double complex y_total = 0.0 + 0.0 * I;

    for (int i = 0; i < num_groups; i++) {
        if (groups[i].count <= 0 || groups[i].c_farad <= 0.0) continue;
        double complex z_branch = calc_branch_z(&groups[i], omega);
        double complex y_branch = 1.0 / z_branch;
        y_total += (double)groups[i].count * y_branch;
    }

    if (cabs(y_total) == 0.0) return 1e9 + 0.0 * I;
    return 1.0 / y_total;
}

/* Симуляція PDN у діапазоні частот */
static void run_pdn_simulation(const CapGroup *groups, int num_groups,
                               double f_start, double f_stop, int points_per_decade,
                               double z_target_ohm) {
    printf("========================================================================\n");
    printf("           СИМУЛЯЦІЯ ІМПЕДАНСНОГО ПРОФІЛЮ ШИНИ ЖИВЛЕННЯ (PDN)           \n");
    printf("========================================================================\n");
    printf("Цільовий імпеданс Z_target: %.2f мОм (%.4f Ом)\n\n", z_target_ohm * 1000.0, z_target_ohm);
    printf("%-12s | %-12s | %-10s | %-10s\n", "Частота", "|Z_PDN| (мОм)", "Фаза (°)", "Статус");
    printf("-------------+--------------+------------+-----------\n");

    double decades = log10(f_stop / f_start);
    int total_pts = (int)(decades * points_per_decade) + 1;
    double step_factor = pow(10.0, 1.0 / (double)points_per_decade);

    double cur_f = f_start;
    double max_z = 0.0;
    double max_z_freq = 0.0;
    int violations = 0;

    for (int p = 0; p < total_pts; p++) {
        double complex z_val = calc_pdn_z(groups, num_groups, cur_f);
        double mag = cabs(z_val);
        double phase = carg(z_val) * (180.0 / M_PI);
        bool viol = (mag > z_target_ohm);

        if (viol) violations++;
        if (mag > max_z) {
            max_z = mag;
            max_z_freq = cur_f;
        }

        /* Друкуємо вибірково точки для звіту (2 точки на декаду) */
        if (p % (points_per_decade / 2) == 0 || viol) {
            const char *unit = "Гц";
            double disp_f = cur_f;
            if (cur_f >= 1e6) { disp_f /= 1e6; unit = "МГц"; }
            else if (cur_f >= 1e3) { disp_f /= 1e3; unit = "кГц"; }

            printf("%7.2f %-4s | %10.3f   | %8.1f°  | %s\n",
                   disp_f, unit, mag * 1000.0, phase,
                   viol ? "УВАГА: ПІК!" : "НОРМА");
        }
        cur_f *= step_factor;
        if (cur_f > f_stop) break;
    }

    printf("------------------------------------------------------------------------\n");
    printf("Максимальний імпеданс: %.3f мОм на частоті %.2f МГц\n",
           max_z * 1000.0, max_z_freq / 1e6);
    if (violations > 0) {
        printf("ВИСНОВОК: Виявлено порушення Z_target! Необхідне демпфування антирезонансу.\n");
    } else {
        printf("ВИСНОВОК: Імпеданс шини живлення відповідає критеріям у всьому діапазоні.\n");
    }
    printf("========================================================================\n\n");
}

int main(void) {
    /* Конфігурація шини FPGA: 0.9 В, 15 А транзієнт, Z_target = 1.8 мОм */
    double z_target = 0.0018; /* 1.8 мОм */

    CapGroup pdn_caps[] = {
        { "Bulk Al-Polymer 470uF", 470e-6, 0.010, 2.5e-9, 0.8e-9, 0.001, 4 },
        { "MLCC 0805 X7R 22uF",    15.0e-6, 0.008, 0.8e-9, 0.5e-9, 0.0005, 10 },
        { "MLCC 0402 X7R 1uF",     0.7e-6,  0.012, 0.4e-9, 0.3e-9, 0.0005, 20 },
        { "MLCC 0201 X7R 100nF",   0.08e-6, 0.018, 0.2e-9, 0.2e-9, 0.0005, 40 }
    };
    int num_groups = sizeof(pdn_caps) / sizeof(pdn_caps[0]);

    run_pdn_simulation(pdn_caps, num_groups, 10e3, 500e6, 20, z_target);
    return 0;
}
