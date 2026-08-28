/* src/calculator.h (C-інтерфейс бібліотеки) */
#ifndef CALCULATOR_H
#define CALCULATOR_H

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    CALC_OK = 0,
    CALC_ERR_DIV_BY_ZERO = 1,
    CALC_ERR_OVERFLOW = 2
} CalcStatus;

CalcStatus calc_divide(double a, double b, double* out_result);
bool calc_write_record(const char* filepath, int key, double value);

#ifdef __cplusplus
}
#endif

#endif
