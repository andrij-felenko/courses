/* src/calculator.c (C-реалізація) */
#include "calculator.h"
#include <stdio.h>

CalcStatus calc_divide(double a, double b, double* out_result) {
    if (!out_result) return CALC_ERR_OVERFLOW;
    if (b == 0.0) return CALC_ERR_DIV_BY_ZERO;
    *out_result = a / b;
    return CALC_OK;
}

bool calc_write_record(const char* filepath, int key, double value) {
    FILE* f = fopen(filepath, "a");
    if (!f) return false;
    fprintf(f, "%d:%f\n", key, value);
    fclose(f);
    return true;
}
