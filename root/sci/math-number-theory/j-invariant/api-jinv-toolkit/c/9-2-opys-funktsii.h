typedef struct {
    double re;
    double im;
} complex64_t;

jinv_status_t jinv_complex_reduce_to_fundamental(
    complex64_t tau_in,
    complex64_t *tau_out
);

jinv_status_t jinv_complex_eval_fourier(
    complex64_t tau,
    complex64_t *j_out,
    int num_terms
);
