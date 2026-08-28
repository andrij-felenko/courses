#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    size_t dim;
    double *data;
} TetrahedralTensor3D;

bool tensor3d_init(TetrahedralTensor3D *tensor, size_t dim) {
    tensor->dim = dim;
    size_t total = dim * (dim + 1) * (dim + 2) / 6;
    tensor->data = (double *)calloc(total, sizeof(double));
    return tensor->data != NULL;
}

void tensor3d_free(TetrahedralTensor3D *tensor) {
    if (tensor->data) {
        free(tensor->data);
        tensor->data = NULL;
    }
    tensor->dim = 0;
}

double tensor3d_get(const TetrahedralTensor3D *tensor, size_t i, size_t j, size_t k) {
    if (k > j || j > i || i >= tensor->dim) return 0.0;
    size_t flat_idx = i * (i + 1) * (i + 2) / 6 + j * (j + 1) / 2 + k;
    return tensor->data[flat_idx];
}
