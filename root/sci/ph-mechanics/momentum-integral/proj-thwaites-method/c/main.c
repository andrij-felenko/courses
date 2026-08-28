#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double x;           /* координата уздовж поверхні, [м] */
    double U_e;         /* зовнішня швидкість, [м/с] */
    double dUe_dx;      /* градієнт зовнішньої швидкості, [1/с] */
    double theta;       /* товщина втрати імпульсу, [м] */
    double delta_star;  /* товщина зміщення, [м] */
    double H;           /* коефіцієнт форми (delta_star / theta) */
    double lambda_T;    /* параметр градієнта тиску Твейтса */
    double C_f;         /* місцевий коефіцієнт тертя */
    int is_separated;   /* прапорець відриву (1 - відрив, 0 - без відриву) */
} thwaites_point_t;

/* Обчислення функцій Твейтса l(lambda) та H(lambda) */
static void thwaites_correlations(double lambda, double *l_out, double *H_out) {
    if (lambda <= -0.09) {
        *l_out = 0.0;
        *H_out = 3.55;
    } else if (lambda <= 0.0) {
        *l_out = 0.225 + 2.3 * lambda - 6.0 * lambda * lambda;
        *H_out = 2.61 - 3.75 * lambda + 80.0 * lambda * lambda;
    } else {
        *l_out = 0.225 + 2.3 * lambda - 2.0 * lambda * lambda;
        *H_out = 2.61 - 3.75 * lambda + 15.0 * lambda * lambda;
    }
}

/* Чисельне інтегрування за методом Твейтса для масиву точок уздовж поверхні */
int thwaites_solve(const double *x, const double *U_e, const double *dUe_dx, 
                   size_t n, double nu, thwaites_point_t *results) {
    if (!x || !U_e || !dUe_dx || !results || n < 2 || nu <= 0.0) {
        return -1;
    }

    double integral_val = 0.0;

    /* Обробка першої точки (точка гальмування x=0 або початок пластини) */
    results[0].x = x[0];
    results[0].U_e = U_e[0];
    results[0].dUe_dx = dUe_dx[0];

    if (U_e[0] < 1e-9) {
        /* Точка гальмування (Stagnation point): lambda_T = 0.075 */
        results[0].lambda_T = 0.075;
        double l_val, H_val;
        thwaites_correlations(0.075, &l_val, &H_val);
        results[0].theta = sqrt(0.075 * nu / (dUe_dx[0] > 1e-9 ? dUe_dx[0] : 1.0));
        results[0].H = H_val;
        results[0].delta_star = results[0].theta * H_val;
        results[0].C_f = 0.0;
        results[0].is_separated = 0;
    } else {
        /* Початок плоскої пластини або задана початкова товщина */
        results[0].theta = 1e-6;
        results[0].lambda_T = (results[0].theta * results[0].theta / nu) * dUe_dx[0];
        double l_val, H_val;
        thwaites_correlations(results[0].lambda_T, &l_val, &H_val);
        results[0].H = H_val;
        results[0].delta_star = results[0].theta * H_val;
        results[0].C_f = 2.0 * nu * l_val / (U_e[0] * results[0].theta);
        results[0].is_separated = 0;
    }

    /* Чисельна квадратура методом трапецій для точок 1..n-1 */
    for (size_t i = 1; i < n; ++i) {
        results[i].x = x[i];
        results[i].U_e = U_e[i];
        results[i].dUe_dx = dUe_dx[i];

        double dx = x[i] - x[i - 1];
        double u_prev_5 = pow(U_e[i - 1], 5.0);
        double u_curr_5 = pow(U_e[i], 5.0);

        /* Трапецієподібний крок квадратури int U_e^5 dx */
        integral_val += 0.5 * (u_prev_5 + u_curr_5) * dx;

        double u_curr_6 = pow(U_e[i], 6.0);
        if (u_curr_6 < 1e-12) {
            u_curr_6 = 1e-12;
        }

        double theta_sq = (0.45 * nu / u_curr_6) * integral_val;
        results[i].theta = sqrt(theta_sq);

        results[i].lambda_T = (theta_sq / nu) * dUe_dx[i];

        if (results[i].lambda_T <= -0.09) {
            results[i].is_separated = 1;
            results[i].H = 3.55;
            results[i].delta_star = results[i].theta * 3.55;
            results[i].C_f = 0.0;
        } else {
            results[i].is_separated = 0;
            double l_val, H_val;
            thwaites_correlations(results[i].lambda_T, &l_val, &H_val);
            results[i].H = H_val;
            results[i].delta_star = results[i].theta * H_val;
            results[i].C_f = 2.0 * nu * l_val / (U_e[i] * results[i].theta);
        }
    }

    return 0;
}
