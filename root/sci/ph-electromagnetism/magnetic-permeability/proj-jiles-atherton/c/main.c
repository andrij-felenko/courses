#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MU_0 1.25663706212e-6  /* Магнітна стала вакууму, Гн/м */

typedef struct {
    double M_s;  /* Намагніченість насичення, А/м */
    double a;    /* Параметр форми кривої Ланжевена, А/м */
    double k;    /* Коефіцієнт піннінгу стінок (коерцитивність), А/м */
    double c;    /* Коефіцієнт зворотності (0..1) */
    double alpha;/* Параметр міждоменного зв'язку */
    double M;    /* Поточна намагніченість, А/м */
    double M_irr;/* Незворотна складова намагніченості, А/м */
} JilesAtherton;

/* Обчислення безгістерезисної намагніченості за функцією Ланжевена */
static double calc_M_an(const JilesAtherton* model, double H_e) {
    if (fabs(H_e) < 1e-6) {
        return 0.0;
    }
    double z = H_e / model->a;
    /* Асимптотика для запобігання переповненню exp(z) */
    if (fabs(z) > 100.0) {
        return model->M_s * (z > 0 ? 1.0 : -1.0);
    }
    double coth_z = 1.0 / tanh(z);
    return model->M_s * (coth_z - 1.0 / z);
}

/* Похідна функції Ланжевена dM_an / dH_e */
static double calc_dM_an_dHe(const JilesAtherton* model, double H_e) {
    if (fabs(H_e) < 1e-6) {
        return model->M_s / (3.0 * model->a);
    }
    double z = H_e / model->a;
    if (fabs(z) > 100.0) {
        return 0.0;
    }
    double sinh_z = sinh(z);
    double coth_z = 1.0 / tanh(z);
    double d_coth = 1.0 - coth_z * coth_z;
    double d_inv_z = -1.0 / (z * z);
    return (model->M_s / model->a) * (d_coth - d_inv_z);
}

/* Один крок чисельного інтегрування методом Ейлера з корекцією знаку */
void ja_step(JilesAtherton* model, double H_next, double dH) {
    if (fabs(dH) < 1e-12) return;

    double delta = (dH > 0.0) ? 1.0 : -1.0;
    double H_e = H_next + model->alpha * model->M;
    double M_an = calc_M_an(model, H_e);
    double dMan_dHe = calc_dM_an_dHe(model, H_e);

    /* Незворотна сприйнятливість dM_irr / dH_e */
    double diff = (M_an - model->M_irr);
    double dMirr_dHe = 0.0;
    
    /* Фізична умова: незворотне перемагнічування відбувається лише назустріч M_an */
    if (delta * diff > 0.0) {
        dMirr_dHe = diff / (delta * model->k);
    }

    /* Розрахунок повної диференціальної сприйнятливості dM/dH */
    double numerator = (1.0 - model->c) * dMirr_dHe + model->c * dMan_dHe;
    double denominator = 1.0 - model->alpha * ((1.0 - model->c) * dMirr_dHe + model->c * dMan_dHe);
    
    double dM_dH = 0.0;
    if (fabs(denominator) > 1e-9) {
        dM_dH = numerator / denominator;
    }
    if (dM_dH < 0.0) {
        dM_dH = 0.0; /* Захист від нефізичних від'ємних диференціальних значень */
    }

    /* Оновлення внутрішніх станів моделі */
    double delta_M = dM_dH * dH;
    model->M += delta_M;
    
    /* Оновлення незворотної складової */
    if (fabs(1.0 - model->c) > 1e-6) {
        model->M_irr = (model->M - model->c * M_an) / (1.0 - model->c);
    }
}

int main(void) {
    JilesAtherton ja = {
        .M_s = 1.6e6,
        .a = 1100.0,
        .k = 400.0,
        .c = 0.2,
        .alpha = 1.6e-3,
        .M = 0.0,
        .M_irr = 0.0
    };

    const int steps_per_cycle = 2000;
    const int total_cycles = 3; /* Кілька циклів для виходу на стабільну граничну петлю */
    const double H_peak = 3000.0; /* Амплітуда напруженості поля, А/м */

    double prev_H = 0.0;
    double prev_B = 0.0;
    double energy_loss_joules_m3 = 0.0;

    printf("# Симуляція петлі гістерезису B(H)\n");
    printf("# H (A/m)\tM (A/m)\tB (Tesla)\tmu_diff\n");

    for (int cycle = 0; cycle < total_cycles; ++cycle) {
        for (int i = 0; i < steps_per_cycle; ++i) {
            double angle = 2.0 * M_PI * (double)i / (double)steps_per_cycle;
            double H = H_peak * sin(angle);
            double dH = H - prev_H;

            ja_step(&ja, H, dH);
            double B = MU_0 * (H + ja.M);

            /* На останньому циклі обчислюємо площу петлі втрат */
            if (cycle == total_cycles - 1) {
                if (i > 0) {
                    /* Метод трапецій для інтеграла ∮ H dB */
                    energy_loss_joules_m3 += 0.5 * (H + prev_H) * (B - prev_B);
                }
                if (i % 40 == 0) {
                    double mu_diff = (fabs(dH) > 1e-6) ? (B - prev_B) / (dH * MU_0) : 1.0;
                    printf("%10.2f\t%10.2f\t%10.4f\t%10.1f\n", H, ja.M, B, mu_diff);
                }
            }

            prev_H = H;
            prev_B = B;
        }
    }

    printf("\n# Підсумок:\n");
    printf("# Енергетичні втрати на перемагнічування: %.2f Дж/м^3 за цикл\n", fabs(energy_loss_joules_m3));
    printf("# Потужність втрат при 50 Гц: %.2f кВт/м^3\n", fabs(energy_loss_joules_m3) * 50.0 / 1000.0);

    return 0;
}
