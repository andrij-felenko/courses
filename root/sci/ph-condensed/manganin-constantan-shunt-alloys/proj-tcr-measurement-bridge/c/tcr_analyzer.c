/* tcr_analyzer.c - Автоматизована компенсація термо-ЕРС та МНК-апроксимація ТКО */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double temp_c;   /* Температура у градусах Цельсія */
    double v_pos;    /* Напруга при прямому струмі (+I), Вольт */
    double v_neg;    /* Напруга при зворотному струмі (-I), Вольт */
} tcr_measurement_t;

typedef struct {
    double r0;       /* Опір при 20 °C, Ом */
    double alpha;    /* Лінійний ТКО, 1/K або ppm/K */
    double beta;     /* Квадратичний ТКО, 1/K^2 або ppm/K^2 */
    double t_max;    /* Температура вершини параболи, °C */
} tcr_fit_result_t;

/* Обчислення істинного опору без паразитної термо-ЕРС */
double compute_true_resistance(double v_pos, double v_neg, double i_test) {
    double v_true = (v_pos - v_neg) / 2.0;
    return v_true / i_test;
}

/* Обчислення паразитної термо-ЕРС, яка була присутня під час вимірювання */
double compute_thermal_emf(double v_pos, double v_neg) {
    return (v_pos + v_neg) / 2.0;
}

/* Квадратична регресія методом найменших квадратів (МНК) для R(T) = R0 * (1 + a*dT + b*dT^2) */
int fit_tcr_parabola(const tcr_measurement_t* data, size_t count, double i_test, tcr_fit_result_t* result) {
    if (!data || count < 3 || !result || i_test <= 0.0) {
        return -1;
    }

    double s0 = 0.0, s1 = 0.0, s2 = 0.0, s3 = 0.0, s4 = 0.0;
    double sy = 0.0, s1y = 0.0, s2y = 0.0;

    for (size_t i = 0; i < count; ++i) {
        double dt = data[i].temp_c - 20.0;
        double r = compute_true_resistance(data[i].v_pos, data[i].v_neg, i_test);

        double dt2 = dt * dt;
        s0 += 1.0;
        s1 += dt;
        s2 += dt2;
        s3 += dt * dt2;
        s4 += dt2 * dt2;

        sy += r;
        s1y += dt * r;
        s2y += dt2 * r;
    }

    /* Розв'язання системи лінійних рівнянь 3x3 за методом Крамера */
    double det = s0 * (s2 * s4 - s3 * s3) - s1 * (s1 * s4 - s2 * s3) + s2 * (s1 * s3 - s2 * s2);
    if (fabs(det) < 1e-12) {
        return -2; /* Вироджена матриця */
    }

    double det_a = sy * (s2 * s4 - s3 * s3) - s1 * (s1y * s4 - s2y * s3) + s2 * (s1y * s3 - s2y * s2);
    double det_b = s0 * (s1y * s4 - s2y * s3) - sy * (s1 * s4 - s2 * s3) + s2 * (s1 * s3 - s2y * s2);
    double det_c = s0 * (s2 * s2y - s1y * s3) - s1 * (s1 * s2y - s1y * s2) + sy * (s1 * s3 - s2 * s2);

    double c0 = det_a / det;  /* R0 */
    double c1 = det_b / det;  /* R0 * alpha */
    double c2 = det_c / det;  /* R0 * beta */

    result->r0 = c0;
    result->alpha = (c1 / c0) * 1e6; /* Переведення у ppm/K */
    result->beta = (c2 / c0) * 1e6;  /* Переведення у ppm/K^2 */
    
    if (fabs(result->beta) > 1e-9) {
        result->t_max = 20.0 - (result->alpha / (2.0 * result->beta));
    } else {
        result->t_max = 20.0;
    }

    return 0;
}
