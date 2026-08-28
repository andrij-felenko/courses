#include <stdio.h>
#include <math.h>
#include <stdbool.h>
#include <stddef.h>

/* Коди результату виконання розрахунку */
typedef enum {
    TC_OK = 0,
    TC_ERR_COLD_JUNCTION_OUT_OF_RANGE,
    TC_ERR_VOLTAGE_OUT_OF_RANGE,
    TC_ERR_SENSOR_BURNOUT
} tc_status_t;

/* Обчислення полінома за схемою Горнера: a[0] + x*a[1] + ... + x^n * a[n] */
static double horner_eval(const double *coeffs, size_t count, double x) {
    double result = coeffs[count - 1];
    for (size_t i = count - 1; i > 0; --i) {
        result = result * x + coeffs[i - 1];
    }
    return result;
}

/* Прямий поліном NIST Type K: T (°C) -> V (мВ) */
static double nist_type_k_temp_to_mv(double temp_c) {
    if (temp_c < 0.0) {
        /* Діапазон -200..0 °C (11 коефіцієнтів) */
        static const double c_neg[] = {
            0.000000000000E+00,  3.945012802500E-02,  2.362237359800E-05,
           -3.285890678400E-07, -4.990482877700E-09, -6.750905917300E-11,
           -5.741032742800E-13, -3.108894161400E-15, -1.045160936500E-17,
           -1.988926677800E-20, -1.632269748600E-23
        };
        return horner_eval(c_neg, sizeof(c_neg) / sizeof(c_neg[0]), temp_c);
    } else {
        /* Діапазон 0..1372 °C (10 коефіцієнтів + експонента) */
        static const double c_pos[] = {
           -1.760041368600E-02,  3.892120497500E-02,  1.855877003200E-05,
           -9.945759287400E-08,  3.184094571900E-10, -5.607284488900E-13,
            5.607505905900E-16, -3.202072444000E-19,  9.715114715200E-23,
           -1.210472127500E-26
        };
        double v = horner_eval(c_pos, sizeof(c_pos) / sizeof(c_pos[0]), temp_c);
        /* Експоненційний доданок для фазового переходу Алюмелю */
        double a0 = 0.1185976;
        double a1 = -0.0001183432;
        double a2 = 126.9686;
        double exp_term = a0 * exp(a1 * (temp_c - a2) * (temp_c - a2));
        return v + exp_term;
    }
}

/* Обернений поліном NIST Type K: V (мВ) -> T (°C) */
static double nist_type_k_mv_to_temp(double mv) {
    if (mv < 0.0) {
        /* Піддіапазон 1: -200..0 °C (-5.891..0.000 мВ, 9 коефіцієнтів) */
        static const double d_sub1[] = {
            0.0000000E+00,  2.5173462E+01, -1.1662878E+00,
           -1.0833638E+00, -8.9773540E-01, -3.7342377E-01,
           -8.6632643E-02, -1.0450598E-02, -5.1920577E-04
        };
        return horner_eval(d_sub1, sizeof(d_sub1) / sizeof(d_sub1[0]), mv);
    } else if (mv <= 20.644) {
        /* Піддіапазон 2: 0..500 °C (0.000..20.644 мВ, 10 коефіцієнтів) */
        static const double d_sub2[] = {
            0.000000E+00,  2.508355E+01,  7.860106E-02,
           -2.503131E-01,  8.315270E-02, -1.228034E-02,
            9.804036E-04, -4.413030E-05,  1.057734E-06,
           -1.052755E-08
        };
        return horner_eval(d_sub2, sizeof(d_sub2) / sizeof(d_sub2[0]), mv);
    } else {
        /* Піддіапазон 3: 500..1372 °C (20.644..54.886 мВ, 7 коефіцієнтів) */
        static const double d_sub3[] = {
           -1.318058E+02,  4.830222E+01, -1.646031E+00,
            5.464731E-02, -9.650715E-04,  8.802193E-06,
           -3.110810E-08
        };
        return horner_eval(d_sub3, sizeof(d_sub3) / sizeof(d_sub3[0]), mv);
    }
}

/* Повний конвеєр розрахунку температури з компенсацією холодного спаю */
tc_status_t thermocouple_type_k_calculate(double raw_mv, double cj_temp_c, double *out_temp_c) {
    /* Перевірка валідності температури холодного спаю (плата від -40 до +85 °C) */
    if (cj_temp_c < -50.0 || cj_temp_c > 125.0) {
        return TC_ERR_COLD_JUNCTION_OUT_OF_RANGE;
    }

    /* Виявлення обриву зонда: резистори підтяжки зміщують вхід вище 60 мВ */
    if (raw_mv > 65.0 || raw_mv < -10.0) {
        return TC_ERR_SENSOR_BURNOUT;
    }

    /* Етап A: Отримуємо еквівалентну напругу холодного спаю */
    double v_cj = nist_type_k_temp_to_mv(cj_temp_c);

    /* Етап B: Додаємо виміряну термо-ЕРС до напруги холодного спаю */
    double v_total = raw_mv + v_cj;

    /* Перевірка допустимих фізичних меж Type K (-5.891 мВ .. 54.886 мВ) */
    if (v_total < -5.891 || v_total > 54.886) {
        return TC_ERR_VOLTAGE_OUT_OF_RANGE;
    }

    /* Етап C: Обчислюємо температуру гарячого спаю через обернений поліном */
    *out_temp_c = nist_type_k_mv_to_temp(v_total);
    return TC_OK;
}
