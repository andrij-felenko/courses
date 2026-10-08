#include <stdio.h>
#include <math.h>
#include <stdbool.h>

typedef enum {
    IEC_CLASS_AA,
    IEC_CLASS_A,
    IEC_CLASS_B,
    IEC_CLASS_C
} iec_tolerance_class_t;

// Обчислення гранично допустимого відхилення температури dt (°C)
double iec60751_get_tolerance_deg_c(iec_tolerance_class_t tol_class, double temp_c) {
    double abs_t = fabs(temp_c);
    switch (tol_class) {
        case IEC_CLASS_AA: return 0.10 + 0.0017 * abs_t;
        case IEC_CLASS_A:  return 0.15 + 0.0020 * abs_t;
        case IEC_CLASS_B:  return 0.30 + 0.0050 * abs_t;
        case IEC_CLASS_C:  return 0.60 + 0.0100 * abs_t;
        default:           return -1.0;
    }
}

// Перевірка, чи вкладається виміряна температура у допуск класу
bool iec60751_is_within_tolerance(double measured_t, double reference_t, iec_tolerance_class_t tol_class) {
    double max_dev = iec60751_get_tolerance_deg_c(tol_class, reference_t);
    return fabs(measured_t - reference_t) <= max_dev;
}
