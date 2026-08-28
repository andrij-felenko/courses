/* Обчислення кореляційного інтегралу C(r) для заданого масиву радіусів */
TakensStatus takens_compute_correlation_integral(
    const TakensEmbedding *embedding,
    const double *r_values,
    size_t r_count,
    double *out_c_r
);

/* Оцінка старшого показника Ляпунова за алгоритмом Розенштейна */
TakensStatus takens_compute_lyapunov_max(
    const TakensEmbedding *embedding,
    size_t theiler_window,
    size_t max_steps,
    double *out_lyapunov_exp
);
