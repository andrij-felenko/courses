#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define A_CC 0.142          // Довжина зв'язку C-C (нм)
#define TIGHT_BINDING_T 2.7 // Інтеграл перескоку (еВ)

typedef struct {
    double x;
    double y;
    double z;
} Atom3D;

typedef struct {
    int n;
    int m;
    double diameter_nm;
    double chiral_angle_deg;
    bool is_metal;
    double band_gap_eV;
} CNTProperties;

static double clamp_val(double val, double min_val, double max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

CNTProperties compute_cnt_properties(int n, int m) {
    CNTProperties props;
    props.n = n;
    props.m = m;

    double a = A_CC * sqrt(3.0);
    double l_circ = a * sqrt((double)(n * n + n * m + m * m));
    props.diameter_nm = l_circ / M_PI;

    double cos_theta = (2.0 * n + m) / (2.0 * sqrt((double)(n * n + n * m + m * m)));
    cos_theta = clamp_val(cos_theta, -1.0, 1.0);
    props.chiral_angle_deg = acos(cos_theta) * (180.0 / M_PI);

    props.is_metal = ((n - m) % 3 == 0);
    props.band_gap_eV = props.is_metal ? 0.0 : (2.0 * A_CC * TIGHT_BINDING_T) / props.diameter_nm;

    return props;
}

int main(void) {
    int n = 10, m = 0;
    CNTProperties props = compute_cnt_properties(n, m);

    printf("Параметри CNT (%d, %d):\n", props.n, props.m);
    printf("  Діаметр: %.4f нм\n", props.diameter_nm);
    printf("  Кут хіральності: %.2f град\n", props.chiral_angle_deg);
    printf("  Тип провідності: %s\n", props.is_metal ? "Метал" : "Напівпровідник");
    printf("  Ширина забороненої зони E_g: %.4f еВ\n", props.band_gap_eV);

    return 0;
}
