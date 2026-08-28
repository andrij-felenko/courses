#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Параметри моделі Джайлса - Атертона для трансформаторної сталі */
typedef struct {
    double Ms;   /* Намагніченість насичення (А/м) */
    double a;    /* Константа поля (А/м) */
    double alpha;/* Параметр міждоменного поля */
    double k;    /* Параметр пиннингу (коерцитивна сила) */
    double c;    /* Коефіцієнт оборотного вигинання */
} ja_params_t;

/* Модифікована функція Ланжевена L(x) = coth(x) - 1/x */
static double langevin(double x) {
    if (fabs(x) < 1e-4) {
        return x / 3.0 - (x * x * x) / 45.0; /* Розклад Тейлора при x -> 0 */
    }
    return (1.0 / tanh(x)) - (1.0 / x);
}

/* Похідна функції Ланжевена dL/dx = 1 - coth^2(x) + 1/x^2 */
static double langevin_der(double x) {
    if (fabs(x) < 1e-4) {
        return 1.0 / 3.0 - (x * x) / 15.0;
    }
    double ct = 1.0 / tanh(x);
    return 1.0 - ct * ct + 1.0 / (x * x);
}

/* Обчислення безгістерезисної намагніченості M_an */
static double calc_Man(double H, double M, const ja_params_t* p) {
    double He = H + p->alpha * M;
    if (fabs(He) < 1e-9) return 0.0;
    return p->Ms * langevin(He / p->a);
}

/* Права частина диференціального рівняння dM/dH */
static double dM_dH(double H, double M, double dir, const ja_params_t* p) {
    double Man = calc_Man(H, M, p);
    double He = H + p->alpha * M;
    double dMan_dHe = (fabs(He) < 1e-9) ? (p->Ms / (3.0 * p->a)) 
                                        : (p->Ms / p->a) * langevin_der(He / p->a);

    double delta = (dir >= 0.0) ? 1.0 : -1.0;
    double den = delta * p->k - p->alpha * (Man - M);

    if (fabs(den) < 1e-9) den = 1e-9;

    double dMirr_dH = (Man - M) / den;

    /* Захист від від'ємного нефізичного приросту необоротної намагніченості */
    if ((dir > 0.0 && dMirr_dH < 0.0) || (dir < 0.0 && dMirr_dH > 0.0)) {
        dMirr_dH = 0.0;
    }

    double dM_dH_val = (dMirr_dH + p->c * dMan_dHe) / (1.0 + p->c * (1.0 - p->alpha * dMan_dHe));
    return dM_dH_val;
}

/* Метод Рунге - Кутти 4-го порядку для кроку по H */
static double rk4_step(double H, double M, double dH, const ja_params_t* p) {
    double dir = (dH >= 0.0) ? 1.0 : -1.0;
    double k1 = dM_dH(H, M, dir, p);
    double k2 = dM_dH(H + 0.5 * dH, M + 0.5 * dH * k1, dir, p);
    double k3 = dM_dH(H + 0.5 * dH, M + 0.5 * dH * k2, dir, p);
    double k4 = dM_dH(H + dH, M + dH * k3, dir, p);

    return M + (dH / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4);
}

int main(void) {
    ja_params_t fe = {
        .Ms = 1.6e6,
        .a = 800.0,
        .alpha = 1.1e-3,
        .k = 500.0,
        .c = 0.15
    };

    int steps = 1000;
    double H_max = 3000.0; /* Максимальне зовнішнє поле (А/м) */
    double M = 0.0;
    double H = 0.0;
    double mu0 = 4.0 * M_PI * 1e-7;

    double loss_Q = 0.0; /* Площа петлі ∮ H dB */
    double M_prev = 0.0;
    double H_prev = 0.0;

    printf("# H(A/m)\tM(A/m)\tB(T)\n");

    /* Повний цикл перемагнічування 0 -> +Hmax -> -Hmax -> +Hmax */
    for (int cycle = 0; cycle < 2; ++cycle) {
        /* Вверх 0 -> Hmax */
        double dH = H_max / steps;
        for (int i = 0; i < steps; ++i) {
            M = rk4_step(H, M, dH, &fe);
            H += dH;
            double B = mu0 * (H + M);
            if (cycle == 1) {
                double dB = B - mu0 * (H_prev + M_prev);
                loss_Q += H * dB;
            }
            H_prev = H; M_prev = M;
        }

        /* Вниз Hmax -> -Hmax */
        dH = -2.0 * H_max / (2 * steps);
        for (int i = 0; i < 2 * steps; ++i) {
            M = rk4_step(H, M, dH, &fe);
            H += dH;
            double B = mu0 * (H + M);
            if (cycle == 1) {
                double dB = B - mu0 * (H_prev + M_prev);
                loss_Q += H * dB;
            }
            H_prev = H; M_prev = M;
        }

        /* Назад -Hmax -> +Hmax */
        dH = 2.0 * H_max / (2 * steps);
        for (int i = 0; i < 2 * steps; ++i) {
            M = rk4_step(H, M, dH, &fe);
            H += dH;
            double B = mu0 * (H + M);
            if (cycle == 1) {
                double dB = B - mu0 * (H_prev + M_prev);
                loss_Q += H * dB;
            }
            H_prev = H; M_prev = M;
            if (cycle == 1 && i % 40 == 0) {
                printf("%.2f\t%.2f\t%.4f\n", H, M, B);
            }
        }
    }

    printf("# Розраховані втрати на гістерезис Q = ∮ H dB: %.2f Дж/м3\n", fabs(loss_Q));
    return 0;
}
