/* mobius.h — Офіційний C-інтерфейс бібліотеки libmobius */
#ifndef MOBIUS_H
#define MOBIUS_H

#include <stddef.h>
#include <stdbool.h>
#include <complex.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    MOBIUS_SUCCESS = 0,
    MOBIUS_ERR_SINGULAR = -1,
    MOBIUS_ERR_INVALID_POINTS = -2,
    MOBIUS_ERR_NULL_POINTER = -3
} MobiusStatus;

typedef enum {
    MOBIUS_PARABOLIC = 0,
    MOBIUS_ELLIPTIC = 1,
    MOBIUS_HYPERBOLIC = 2,
    MOBIUS_LOXODROMIC = 3
} MobiusType;

typedef struct {
    double complex a;
    double complex b;
    double complex c;
    double complex d;
} MobiusTransform;

/* Публічні прототипи функцій */
MobiusTransform mobius_create(double complex a, double complex b, double complex c, double complex d);
MobiusStatus mobius_normalize(const MobiusTransform *in_m, MobiusTransform *out_m);
MobiusStatus mobius_from_three_points(double complex z1, double complex z2, double complex z3,
                                       double complex w1, double complex w2, double complex w3,
                                       MobiusTransform *out_m);

MobiusStatus mobius_compose(const MobiusTransform *m1, const MobiusTransform *m2, MobiusTransform *out_result);
MobiusStatus mobius_inverse(const MobiusTransform *in_m, MobiusTransform *out_inv);
double complex mobius_det(const MobiusTransform *m);
double complex mobius_trace(const MobiusTransform *m);

double complex mobius_eval(const MobiusTransform *m, double complex z, bool *out_is_infinity);
MobiusStatus mobius_eval_array(const MobiusTransform *m, const double complex *in_z,
                               double complex *out_w, bool *out_is_inf_flags, size_t count);

int mobius_fixed_points(const MobiusTransform *m, double complex out_points[2], bool out_is_inf[2]);
double complex mobius_cross_ratio(double complex z1, double complex z2, double complex z3, double complex z4);
MobiusType mobius_classify(const MobiusTransform *m);

#ifdef __cplusplus
}
#endif

#endif /* MOBIUS_H */
