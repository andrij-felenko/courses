typedef struct {
    fp2_t coeffs[8]; /* Коефіцієнти полінома ступеня <= 7 */
    int degree;
} poly_fp2_t;

jinv_status_t poly_fp2_find_roots(
    poly_fp2_t poly,
    fp2_t *roots_out,
    int *num_roots,
    int64_t p
);
