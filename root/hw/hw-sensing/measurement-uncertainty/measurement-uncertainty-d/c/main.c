#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

/* Структура однопрохідного накопичувача Велфорда */
typedef struct {
    uint32_t count;
    double mean;
    double m2; /* Накопичена сума квадратів різниць (x_i - mean) */
} welford_stat_t;

void welford_reset(welford_stat_t *s) {
    s->count = 0;
    s->mean = 0.0;
    s->m2 = 0.0;
}

/* Додавання вибірки: O(1) за часом та пам'яттю */
void welford_push(welford_stat_t *s, double x) {
    s->count++;
    double delta = x - s->mean;
    s->mean += delta / (double)s->count;
    double delta2 = x - s->mean;
    s->m2 += delta * delta2;
}

/* Розрахунок стандартної невизначеності типу A: s / sqrt(N) */
bool welford_result(const welford_stat_t *s, double *mean_out, double *u_a_out) {
    if (s->count < 2) return false;
    *mean_out = s->mean;
    double sample_variance = s->m2 / (double)(s->count - 1);
    *u_a_out = sqrt(sample_variance / (double)s->count);
    return true;
}

/* Перетворення допуску типу B: прямокутний розподіл a / sqrt(3) */
double unc_type_b_rect(double half_width) {
    return half_width / sqrt(3.0);
}

/* Обчислення розширеної невизначеності каналу */
double calc_expanded_uncertainty(double u_a, double u_b_rect, double k_cov) {
    double u_combined = sqrt(u_a * u_a + u_b_rect * u_b_rect);
    return k_cov * u_combined;
}

int main(void) {
    welford_stat_t stat;
    welford_reset(&stat);

    const double adc_samples[8] = {1.254, 1.253, 1.255, 1.254, 1.254, 1.253, 1.255, 1.254};
    for (size_t i = 0; i < 8; ++i) {
        welford_push(&stat, adc_samples[i]);
    }

    double mean_v = 0.0, u_a_v = 0.0;
    if (welford_result(&stat, &mean_v, &u_a_v)) {
        double u_b_v = unc_type_b_rect(0.001); /* Паспортний допуск +/- 1 мВ */
        double u_exp = calc_expanded_uncertainty(u_a_v, u_b_v, 2.0);

        printf("Напруга: %.4f V, Розширена невизначеність U(k=2): +/- %.4f V\n", mean_v, u_exp);
    }
    return 0;
}
