/* Генерація затримкової матриці мовою C */
typedef struct {
    double *data;
    size_t rows;
    size_t cols;
} DelayMatrixC;

DelayMatrixC create_delay_matrix_c(const double *signal, size_t n, size_t m, size_t delay) {
    DelayMatrixC mat = {NULL, 0, 0};
    if (!signal || n <= (m - 1) * delay) return mat;

    size_t n_eff = n - (m - 1) * delay;
    mat.data = (double*)malloc(n_eff * m * sizeof(double));
    if (!mat.data) return mat;

    mat.rows = n_eff;
    mat.cols = m;

    for (size_t i = 0; i < n_eff; ++i) {
        for (size_t j = 0; j < m; ++j) {
            mat.data[i * m + j] = signal[i + j * delay];
        }
    }
    return mat;
}

void free_delay_matrix_c(DelayMatrixC *mat) {
    if (mat && mat->data) {
        free(mat->data);
        mat->data = NULL;
        mat->rows = 0;
        mat->cols = 0;
    }
}
