#include <stdio.h>
#include <math.h>

// Базові мантиси номіналів стандартного ряду E24
static const double E24_MANTISSAS[24] = {
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
};

// Функція квантування до найближчого номіналу ряду E24
double find_closest_e24(double value) {
    if (value <= 0.0) return 0.0;
    double exp_val = floor(log10(value));
    double mantissa = value / pow(10.0, exp_val);

    double best_mantissa = E24_MANTISSAS[0];
    double min_delta = fabs(mantissa - E24_MANTISSAS[0]);

    for (int i = 1; i < 24; ++i) {
        double delta = fabs(mantissa - E24_MANTISSAS[i]);
        if (delta < min_delta) {
            min_delta = delta;
            best_mantissa = E24_MANTISSAS[i];
        }
    }
    return best_mantissa * pow(10.0, exp_val);
}

typedef struct {
    double c_exact;        // Точна розрахункова ємність, Ф
    double c_standard;     // Стандартна ємність з ряду E24, Ф
    double r_exact;        // Точний характеристичний опір, Ом
    double r_standard;     // Стандартний опір з ряду E24, Ом
    double p_resistor_w;   // Необхідна потужність резистора з 2-кратним запасом, Вт
} SnubberDesignOutput;

SnubberDesignOutput design_rc_snubber(double v_cc, double i_load, double l_ind, double f_sw, double v_max_allowable) {
    SnubberDesignOutput out;
    double delta_v_sq = (v_max_allowable * v_max_allowable) - (v_cc * v_cc);
    if (delta_v_sq <= 0.0) delta_v_sq = 1.0;
    
    out.c_exact = (l_ind * i_load * i_load) / delta_v_sq;
    out.c_standard = find_closest_e24(out.c_exact);

    out.r_exact = sqrt(l_ind / out.c_standard);
    out.r_standard = find_closest_e24(out.r_exact);

    // Втрати потужності: P = C * V_cc^2 * f_sw * Margin (2.0)
    out.p_resistor_w = out.c_standard * v_cc * v_cc * f_sw * 2.0;

    return out;
}
