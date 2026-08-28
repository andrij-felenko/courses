#include <stdio.h>
#include <math.h>

/* Обернений поліном NIST ITS-90 для типу K: ЕРС (мВ) -> T (°C) у діапазоні 0..500 °C */
static const double K_INV_POLY[] = {
     0.0000000E+00,
     2.5083550E+01,
     7.8601060E-02,
    -2.5031310E-01,
     8.3152700E-02,
    -1.2280340E-02,
     9.8040360E-04,
    -4.4130300E-05,
     1.0577340E-06,
    -1.0527550E-08
};

/* Пряме лінійне наближення термо-ЕРС біля кімнатної температури (40.7 мкВ/°C) */
double type_k_approx_cjc_uv(double ambient_c) {
    return ambient_c * 40.73;
}

double type_k_calc_temperature_c(double measured_uv, double ambient_temp_c) {
    /* 1. Додаємо еквівалентну ЕРС холодного спаю */
    double v_cjc_uv = type_k_approx_cjc_uv(ambient_temp_c);
    double v_total_mv = (measured_uv + v_cjc_uv) * 1e-3;

    /* 2. Обчислюємо поліном за схемою Горнера для мінімізації множень */
    double temp = K_INV_POLY[9];
    for (int i = 8; i >= 0; --i) {
        temp = temp * v_total_mv + K_INV_POLY[i];
    }
    return temp;
}
