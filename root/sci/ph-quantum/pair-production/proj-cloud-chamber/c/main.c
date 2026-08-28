#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define C_SPEED 2.99792458e8     /* м/с */
#define ELECTRON_MASS_KG 9.1093837015e-31  /* кг */
#define ELECTRON_CHARGE_C 1.602176634e-19  /* Кл */
#define MEV_TO_JOULE 1.602176634e-13

typedef struct {
    double x;
    double y;
    double vx;
    double vy;
    double charge;
} Particle;

void simulate_track(Particle *p, double B, double dt, int steps, const char *filename) {
    FILE *f = fopen(filename, "w");
    if (!f) return;

    fprintf(f, "x,y\n");
    for (int i = 0; i < steps; ++i) {
        fprintf(f, "%.6f,%.6f\n", p->x, p->y);

        double v_sq = p->vx * p->vx + p->vy * p->vy;
        double beta_sq = v_sq / (C_SPEED * C_SPEED);
        if (beta_sq >= 1.0) beta_sq = 0.999999;
        double gamma = 1.0 / sqrt(1.0 - beta_sq);

        /* Сила Лоренца: Fx = q * vy * B, Fy = -q * vx * B */
        double Fx = p->charge * ELECTRON_CHARGE_C * p->vy * B;
        double Fy = -p->charge * ELECTRON_CHARGE_C * p->vx * B;

        /* Прискорення з урахуванням релятивістської маси m = gamma * m_e */
        double ax = Fx / (gamma * ELECTRON_MASS_KG);
        double ay = Fy / (gamma * ELECTRON_MASS_KG);

        p->vx += ax * dt;
        p->vy += ay * dt;

        p->x += p->vx * dt;
        p->y += p->vy * dt;
    }
    fclose(f);
}

int main(void) {
    double E_gamma_MeV = 5.0;  /* Енергія фотона 5 МеВ */
    double B_field = 0.5;       /* Магнітне поле 0.5 Тесла */

    double m_e_c2_MeV = 0.51099895;
    if (E_gamma_MeV < 2.0 * m_e_c2_MeV) {
        printf("Помилка: енергія фотона нижче порога 1.022 МеВ\n");
        return 1;
    }

    double E_kin_total = E_gamma_MeV - 2.0 * m_e_c2_MeV;
    /* Припускаємо симетричний розподіл енергії */
    double E_kin_e = E_kin_total / 2.0;

    double E_total_J = (E_kin_e + m_e_c2_MeV) * MEV_TO_JOULE;
    double gamma = E_total_J / (ELECTRON_MASS_KG * C_SPEED * C_SPEED);
    double beta = sqrt(1.0 - 1.0 / (gamma * gamma));
    double v0 = beta * C_SPEED;

    double p_joule_s = gamma * ELECTRON_MASS_KG * v0;
    double radius = p_joule_s / (ELECTRON_CHARGE_C * B_field);

    printf("Енергія фотона: %.3f МеВ\n", E_gamma_MeV);
    printf("Кінетична енергія електрона/позитрона: %.3f МеВ\n", E_kin_e);
    printf("Лоренц-фактор γ: %.4f\n", gamma);
    printf("Розрахунковий радіус кривизни R: %.4f м\n", radius);

    Particle electron = {0.0, 0.0, 0.0, v0, -1.0};
    Particle positron = {0.0, 0.0, 0.0, v0, +1.0};

    simulate_track(&electron, B_field, 1e-11, 1000, "electron_track.csv");
    simulate_track(&positron, B_field, 1e-11, 1000, "positron_track.csv");

    return 0;
}
