#include "mobius.h"
#include <stdio.h>
#include <stdlib.h>

void process_hydro_grid(const double complex *grid_in, double complex *grid_out, size_t count) {
    MobiusTransform m = mobius_create(1.0, -1.0, 1.0, 1.0);
    MobiusTransform norm;
    if (mobius_normalize(&m, &norm) != MOBIUS_SUCCESS) {
        fprintf(stderr, "Помилка нормалізації матриці гідродінамічного потоку\n");
        return;
    }

    bool *inf_flags = (bool*)malloc(count * sizeof(bool));
    if (!inf_flags) return;

    mobius_eval_array(&norm, grid_in, grid_out, inf_flags, count);
    free(inf_flags);
}
