#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Фізичні константи потенціалу Корнелла
#define ALPHA_S 0.35            // Константа сильного зв'язку
#define K_STRING 1.0            // Натяг струни K (GeV/fm)
#define MASS_QUARK 0.35         // Ефективна маса кварка (GeV)
#define THRESHOLD_PAIR (2.0 * MASS_QUARK) // Поріг народження пари (GeV)

typedef struct {
    double r_fm;                // Відстань між кварками (fm)
    double v_coulomb;           // Кулонівська частина (GeV)
    double v_string;            // Струнна частина (GeV)
    double v_total;             // Повний потенціал Корнелла (GeV)
    double prob_break;          // Ймовірність розриву струни
    int is_broken;              // Прапорець розриву струни
} QcdState;

// Розрахунок потенціалу Корнелла V(r) = -4/3 * alpha_s / r + K * r
double compute_cornell_potential(double r_fm, double *v_coul, double *v_str) {
    if (r_fm <= 0.0) return 0.0;
    *v_coul = -(4.0 / 3.0) * (ALPHA_S / r_fm);
    *v_str = K_STRING * r_fm;
    return (*v_coul) + (*v_str);
}

// Розрахунок ймовірності розриву струни Швінгера
double compute_schwinger_breaking(double v_total) {
    if (v_total < THRESHOLD_PAIR) {
        return 0.0;
    }
    double delta_e = v_total - THRESHOLD_PAIR;
    double rate = 0.85; // Коефіцієнт квантового тунелювання
    return 1.0 - exp(-rate * delta_e);
}

int main(void) {
    const int num_steps = 25;
    const double r_start = 0.1;
    const double r_end = 2.5;
    const double dr = (r_end - r_start) / (num_steps - 1);

    QcdState *trajectory = (QcdState *)malloc(num_steps * sizeof(QcdState));
    if (!trajectory) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    printf("=== МОДЕЛЮВАННЯ ПОТЕНЦІАЛУ КХД ТА РОЗРИВУ СТРУНИ ===\n");
    printf("%-8s | %-10s | %-10s | %-10s | %-10s | %-10s\n",
           "r (fm)", "V_coul(GeV)", "V_str(GeV)", "V_tot(GeV)", "P_break", "Стан");
    printf("-------------------------------------------------------------------\n");

    int string_broken_flag = 0;
    for (int i = 0; i < num_steps; ++i) {
        double r = r_start + i * dr;
        double v_coul = 0.0, v_str = 0.0;
        double v_tot = compute_cornell_potential(r, &v_coul, &v_str);
        double p_break = compute_schwinger_breaking(v_tot);

        trajectory[i].r_fm = r;
        trajectory[i].v_coulomb = v_coul;
        trajectory[i].v_string = v_str;
        trajectory[i].v_total = v_tot;
        trajectory[i].prob_break = p_break;

        if (!string_broken_flag && p_break > 0.65) {
            string_broken_flag = 1;
        }
        trajectory[i].is_broken = string_broken_flag;

        printf("%-8.2f | %-10.4f | %-10.4f | %-10.4f | %-10.4f | %s\n",
               r, v_coul, v_str, v_tot, p_break,
               string_broken_flag ? "РОЗРИВ (Jet)" : "Струна q-qbar");
    }

    free(trajectory);
    return 0;
}
