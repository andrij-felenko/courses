/* conversion_si2019.c — Обчислення квантових еталонних величин SI-2019 */
#include <stdio.h>

/* Фіксовані фундаментальні константи SI 2019 */
static const double CONST_H = 6.62607015e-34;  /* Дж·с (кг·м²/с) */
static const double CONST_E = 1.602176634e-19; /* Кл (А·с) */

/* Обчислення сталої Джозефсона KJ = 2e / h (Гц/В) */
double get_josephson_constant(void) {
    return (2.0 * CONST_E) / CONST_H;
}

/* Обчислення сталої фон Клітцинга RK = h / e² (Ом) */
double get_von_klitzing_constant(void) {
    return CONST_H / (CONST_E * CONST_E);
}

/* Напруга Джозефсона для n переходу на частоті f_hz */
double josephson_voltage(unsigned long long n, double f_hz) {
    double kj = get_josephson_constant();
    return (double)n * f_hz / kj;
}

/* Опір Холла для плато i */
double hall_resistance(unsigned long long plateau_i) {
    if (plateau_i == 0) return 0.0;
    double rk = get_von_klitzing_constant();
    return rk / (double)plateau_i;
}

int main(void) {
    double kj = get_josephson_constant();
    double rk = get_von_klitzing_constant();

    printf("KJ = %.9e Hz/V\n", kj);
    printf("RK = %.9f Ohm\n", rk);

    /* Приклад: 10 000 переходів Джозефсона на частоті 75 ГГц */
    double v_out = josephson_voltage(10000ULL, 75.0e9);
    printf("V_out (10k transitions @ 75 GHz) = %.10f V\n", v_out);

    /* Приклад: Квантовий опір Холла на плато i = 2 */
    double r_out = hall_resistance(2ULL);
    printf("R_out (Hall plateau i=2) = %.9f Ohm\n", r_out);

    return 0;
}
