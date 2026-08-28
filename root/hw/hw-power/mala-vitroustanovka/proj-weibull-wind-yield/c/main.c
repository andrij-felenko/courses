#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double rated_power_w;   /* Номінальна електрична потужність (Вт) */
    double v_cut_in;        /* Швидкість увімкнення (м/с) */
    double v_rated;         /* Номінальна швидкість виходу на потужність (м/с) */
    double v_cut_out;       /* Швидкість аварійного гальмування (м/с) */
    double rotor_radius_m;  /* Радіус ротора (м) */
    double cp_max;          /* Максимальний аеродинамічний ККД ротора */
    double eta_gen;         /* Сумарний ККД генератора, підшипників та випрямляча */
} WindTurbine;

typedef struct {
    double shape_k;         /* Безрозмірний параметр форми k */
    double scale_c;         /* Масштабний параметр швидкості c (м/с) */
    double air_density;     /* Фактична густина повітря (кг/м3, стандарт 1.225) */
} WindClimate;

typedef struct {
    double aep_kwh;         /* Річний виробіток енергії (кВт·год/рік) */
    double avg_power_w;     /* Середньорічна вихідна потужність (Вт) */
    double capacity_factor; /* Коефіцієнт використання потужності (CF, 0..1) */
    double hours_operating; /* Кількість годин генерації за рік */
} WindYieldResult;

/* Густина ймовірності розподілу Вейбулла f(v; k, c) */
double weibull_pdf(double v, double k, double c) {
    if (v <= 0.0 || c <= 0.0 || k <= 0.0) {
        return 0.0;
    }
    double v_c = v / c;
    return (k / c) * pow(v_c, k - 1.0) * exp(-pow(v_c, k));
}

/* Модель вихідної потужності генератора P(v) з урахуванням аеродинаміки та ККД */
double turbine_electrical_power(const WindTurbine *t, const WindClimate *w, double v) {
    if (v < t->v_cut_in || v > t->v_cut_out) {
        return 0.0;
    }
    if (v >= t->v_rated) {
        return t->rated_power_w;
    }
    /* Розрахунок площі обметання: A = pi * R^2 */
    double area = M_PI * t->rotor_radius_m * t->rotor_radius_m;
    /* Аеродинамічна потужність на валу: P = 0.5 * rho * A * v^3 * Cp * eta */
    double p_aero = 0.5 * w->air_density * area * pow(v, 3.0) * t->cp_max * t->eta_gen;

    if (p_aero > t->rated_power_w) {
        p_aero = t->rated_power_w;
    }
    return p_aero;
}

/* Чисельний розрахунок річної генерації за складеним правилом трапецій */
WindYieldResult calculate_annual_yield(const WindTurbine *t, const WindClimate *w) {
    const double v_max = 35.0;     /* Верхня межа інтегрування за швидкістю (м/с) */
    const int steps = 1400;        /* Кількість інтервалів: dv = 35.0 / 1400 = 0.025 м/с */
    const double dv = v_max / (double)steps;
    const double hours_per_year = 8760.0;

    double sum_power_weighted = 0.0;
    double sum_prob_operating = 0.0;

    for (int i = 0; i <= steps; ++i) {
        double v = i * dv;
        double pdf = weibull_pdf(v, w->shape_k, w->scale_c);
        double p_el = turbine_electrical_power(t, w, v);

        double weight = (i == 0 || i == steps) ? 0.5 : 1.0;
        sum_power_weighted += weight * (p_el * pdf);

        if (v >= t->v_cut_in && v <= t->v_cut_out) {
            sum_prob_operating += weight * pdf;
        }
    }

    double avg_power = sum_power_weighted * dv;
    double aep_wh = avg_power * hours_per_year;
    double prob_oper = sum_prob_operating * dv;

    WindYieldResult res;
    res.avg_power_w = avg_power;
    res.aep_kwh = aep_wh / 1000.0;
    res.capacity_factor = avg_power / t->rated_power_w;
    res.hours_operating = prob_oper * hours_per_year;
    return res;
}

int main(void) {
    WindTurbine turbine = {
        .rated_power_w = 1000.0,   /* 1000 Вт номіналу */
        .v_cut_in = 3.0,          /* 3.0 м/с швидкість старту */
        .v_rated = 11.0,          /* 11.0 м/с вихід на повну потужність */
        .v_cut_out = 24.0,        /* 24.0 м/с штормове гальмування */
        .rotor_radius_m = 1.4,    /* Радіус 1.4 м (діаметр 2.8 м, площа 6.16 м2) */
        .cp_max = 0.42,           /* Трилопатевий ротор із профілем NACA */
        .eta_gen = 0.85           /* Сумарний ККД генератора та випрямляча */
    };

    WindClimate climate = {
        .shape_k = 2.05,          /* Параметр форми Вейбулла (помірний вітер) */
        .scale_c = 6.20,          /* Масштабний параметр (середня швидкість ~5.5 м/с) */
        .air_density = 1.225      /* Густина повітря на рівні моря при 15 °C */
    };

    WindYieldResult res = calculate_annual_yield(&turbine, &climate);

    printf("=== Розрахунок річної генерації малої вітроустановки ===\n");
    printf("Номінальна потужність:      %.0f Вт\n", turbine.rated_power_w);
    printf("Діаметр ротора:             %.2f м (площа: %.2f м2)\n",
           turbine.rotor_radius_m * 2.0, M_PI * turbine.rotor_radius_m * turbine.rotor_radius_m);
    printf("Параметри вітру Вейбулла:   k = %.2f, c = %.2f м/с\n", climate.shape_k, climate.scale_c);
    printf("Густина повітря:            %.3f кг/м3\n", climate.air_density);
    printf("----------------------------------------------------\n");
    printf("Середньорічна потужність:   %.1f Вт\n", res.avg_power_w);
    printf("Річна генерація (AEP):      %.1f кВт·год/рік\n", res.aep_kwh);
    printf("Коефіцієнт потужності (CF): %.2f %% (КВВП)\n", res.capacity_factor * 100.0);
    printf("Час активної генерації:     %.0f годин/рік (%.1f %% часу)\n",
           res.hours_operating, (res.hours_operating / 8760.0) * 100.0);

    return 0;
}
