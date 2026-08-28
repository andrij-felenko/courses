#include <stdio.h>
#include <math.h>
#include <stdbool.h>

typedef struct {
    double r20;       /* Опір при 20 °C, Ом */
    double alpha20;   /* Лінійний ТКО, 1/К */
    double beta;      /* Квадратичний ТКО, 1/К² */
    double r_th;      /* Тепловий опір охолодження, К/Вт */
    double t_ambient; /* Температура довкілля, °C */
} AlloyParams;

typedef struct {
    double r_fitted_0;
    double alpha_fitted;
    double beta_fitted;
    double t_peak;
} FitResult;

/* Обчислення опору сплаву при температурі T */
double calculate_resistance(const AlloyParams* alloy, double temp_c) {
    double dt = temp_c - 20.0;
    return alloy->r20 * (1.0 + alloy->alpha20 * dt + alloy->beta * dt * dt);
}

/* Симуляція самонагріву шунта струмом I (ітераційне знаходження теплової рівноваги) */
double simulate_self_heating(const AlloyParams* alloy, double current_a) {
    double temp = alloy->t_ambient;
    for (int iter = 0; iter < 10; ++iter) {
        double r_current = calculate_resistance(alloy, temp);
        double power_w = current_a * current_a * r_current;
        double new_temp = alloy->t_ambient + power_w * alloy->r_th;
        if (fabs(new_temp - temp) < 1e-6) {
            break;
        }
        temp = new_temp;
    }
    return temp;
}

/* МНК-фітинг параболічної залежності за виміряними точками (T_i, R_i) */
bool fit_tcr_parabola(const double* temp_array, const double* r_array, int count, FitResult* result) {
    if (count < 3 || !temp_array || !r_array || !result) {
        return false;
    }

    double s0 = count, s1 = 0, s2 = 0, s3 = 0, s4 = 0;
    double y0 = 0, y1 = 0, y2 = 0;

    for (int i = 0; i < count; ++i) {
        double x = temp_array[i] - 20.0;
        double x2 = x * x;
        double y = r_array[i];

        s1 += x;
        s2 += x2;
        s3 += x2 * x;
        s4 += x2 * x2;

        y0 += y;
        y1 += y * x;
        y2 += y * x2;
    }

    /* Розв'язання системи 3x3 методом Крамера */
    double det = s0 * (s2 * s4 - s3 * s3) - s1 * (s1 * s4 - s2 * s3) + s2 * (s1 * s3 - s2 * s2);
    if (fabs(det) < 1e-15) {
        return false;
    }

    double det_a0 = y0 * (s2 * s4 - s3 * s3) - s1 * (y1 * s4 - s3 * y2) + s2 * (y1 * s3 - s2 * y2);
    double det_a1 = s0 * (y1 * s4 - s3 * y2) - y0 * (s1 * s4 - s2 * s3) + s2 * (s1 * y2 - y1 * s2);
    double det_a2 = s0 * (s2 * y2 - y1 * s3) - s1 * (s1 * y2 - y1 * s2) + y0 * (s1 * s3 - s2 * s2);

    double a0 = det_a0 / det;
    double a1 = det_a1 / det;
    double a2 = det_a2 / det;

    result->r_fitted_0 = a0;
    result->alpha_fitted = a1 / a0;
    result->beta_fitted = a2 / a0;
    result->t_peak = 20.0 - (result->alpha_fitted / (2.0 * result->beta_fitted));

    return true;
}

int main(void) {
    /* Параметри манганінового шунта 1 мОм */
    AlloyParams manganin = {
        .r20 = 0.001,         /* 1 мОм */
        .alpha20 = 2e-6,      /* +2 ppm/K */
        .beta = -4e-7,        /* -0.4 ppm/K² */
        .r_th = 15.0,         /* 15 K/Вт */
        .t_ambient = 25.0
    };

    printf("=== Симуляція манганінового шунта ===\n");
    double current = 50.0; /* 50 А */
    double t_eq = simulate_self_heating(&manganin, current);
    double r_eq = calculate_resistance(&manganin, t_eq);
    double dr_ppm = (r_eq - manganin.r20) / manganin.r20 * 1e6;

    printf("Струм: %.1f А -> Т_рівн: %.2f °C, R: %.7f Ом (Зсув: %.2f ppm)\n\n",
           current, t_eq, r_eq, dr_ppm);

    /* Фітинг ТКО за калібрувальними точками */
    double test_temps[] = {0.0, 15.0, 25.0, 40.0, 60.0};
    double test_res[5];
    for (int i = 0; i < 5; ++i) {
        test_res[i] = calculate_resistance(&manganin, test_temps[i]);
    }

    FitResult fit;
    if (fit_tcr_parabola(test_temps, test_res, 5, &fit)) {
        printf("=== Результати МНК-фітингу ===\n");
        printf("R20: %.6f Ом\n", fit.r_fitted_0);
        printf("Alpha20: %.3f ppm/K\n", fit.alpha_fitted * 1e6);
        printf("Beta: %.4f ppm/K²\n", fit.beta_fitted * 1e6);
        printf("Вершина параболи (T_peak): %.2f °C\n", fit.t_peak);
    }

    return 0;
}
