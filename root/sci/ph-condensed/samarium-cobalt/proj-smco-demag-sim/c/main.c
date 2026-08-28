#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define MU_0 1.2566370614359173e-6 /* Гн/м */

typedef struct {
    double br_20c;    /* B_r при 20 °C, Тл */
    double hcj_20c;   /* H_cj при 20 °C, А/м */
    double alpha_br;  /* Темп. коеф. B_r, %/°C */
    double beta_hcj;  /* Темп. коеф. H_cj, %/°C */
    double mu_rec;    /* Проникність повернення (1.03-1.05) */
    double tc;        /* Температура Кюрі, °C */
} SmCoProperties;

typedef struct {
    double B_d;         /* Робоча індукція, Тл */
    double H_d;         /* Робоче поле, А/м */
    double pc;          /* Коефіцієнт навантаження P_c = -B/(mu0*H) */
    bool is_demagged;   /* Прапорець незворотного розмагнічування */
} OperatingPoint;

/* Конструктори типових марок */
static const SmCoProperties SMCO_1_5 = {
    .br_20c = 0.98,
    .hcj_20c = 1591500.0, /* ~20 кЕ */
    .alpha_br = -0.045,
    .beta_hcj = -0.25,
    .mu_rec = 1.05,
    .tc = 727.0
};

static const SmCoProperties SMCO_2_17 = {
    .br_20c = 1.12,
    .hcj_20c = 1989400.0, /* ~25 кЕ */
    .alpha_br = -0.032,
    .beta_hcj = -0.18,
    .mu_rec = 1.03,
    .tc = 820.0
};

/* Розрахунок робочої точки за даної температури та розмагнічувального фактора Nd */
bool calculate_operating_point(const SmCoProperties *prop, double temp_c, 
                               double Nd, OperatingPoint *out_op) {
    if (!prop || !out_op || Nd <= 0.0 || Nd >= 1.0) {
        return false;
    }

    if (temp_c >= prop->tc) {
        out_op->B_d = 0.0;
        out_op->H_d = 0.0;
        out_op->pc = 0.0;
        out_op->is_demagged = true;
        return true;
    }

    /* Температурний перерахунок параметрів */
    double dT = temp_c - 20.0;
    double br_t = prop->br_20c * (1.0 + (prop->alpha_br / 100.0) * dT);
    double hcj_t = prop->hcj_20c * (1.0 + (prop->beta_hcj / 100.0) * dT);

    if (br_t < 0.0) br_t = 0.0;
    if (hcj_t < 0.0) hcj_t = 0.0;

    /* Похил лінії навантаження: B = - mu0 * Pc * H, де Pc = (1 - Nd) / Nd */
    double Pc = (1.0 - Nd) / Nd;
    out_op->pc = Pc;

    /* Рівняння перетину: B_r(T) + mu0*mu_rec*H = - mu0*Pc*H */
    /* H_d = - B_r(T) / (mu0 * (Pc + mu_rec)) */
    double denom = MU_0 * (Pc + prop->mu_rec);
    out_op->H_d = - br_t / denom;
    out_op->B_d = - MU_0 * Pc * out_op->H_d;

    /* Перевірка чи розмагнічувальне поле не перевищує критичне H_cj(T) */
    out_op->is_demagged = (fabs(out_op->H_d) >= hcj_t);

    return true;
}

int main(void) {
    printf("=== Симуляція робочої точки SmCo2:17 при нагріванні ===\n");
    printf("Т (°C) | B_d (Тл) | -H_d (кА/м) | P_c   | Стан\n");
    printf("---------------------------------------------------\n");

    double Nd = 0.2; /* Типовий циліндр L/D ≈ 1 */
    double temps[] = { 20.0, 150.0, 300.0, 450.0, 550.0 };
    size_t n_temps = sizeof(temps) / sizeof(temps[0]);

    for (size_t i = 0; i < n_temps; ++i) {
        OperatingPoint op;
        if (calculate_operating_point(&SMCO_2_17, temps[i], Nd, &op)) {
            printf("%6.1f | %8.4f | %11.1f | %5.2f | %s\n",
                   temps[i], op.B_d, -op.H_d / 1000.0, op.pc,
                   op.is_demagged ? "РОЗМАГНІЧЕНО" : "ОК (Лінійний)");
        }
    }

    return 0;
}
