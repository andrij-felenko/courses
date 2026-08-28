/* C ABI Сигнатури функцій бібліотеки libmathieu */

/* Управління конфігурацією */
MathieuConfig mathieu_config_default(void);

/* Обчислення монодромії та аналіз точки (q, a) */
MathieuStatus mathieu_analyze_point(
    double a, double q,
    const MathieuConfig* config,
    MathieuPointResult* result
);

MathieuStatus mathieu_compute_monodromy(
    double a, double q, double z_period,
    const MathieuConfig* config,
    double monodromy_out[2][2]
);

/* Обчислення власних значень a_n(q) та b_n(q) */
MathieuStatus mathieu_eigenvalue_a(
    int order_n, double q,
    const MathieuConfig* config,
    double* a_out
);

MathieuStatus mathieu_eigenvalue_b(
    int order_n, double q,
    const MathieuConfig* config,
    double* b_out
);

/* Управління сіткою стійкості */
MathieuStatus mathieu_grid_allocate(
    size_t a_res, size_t q_res,
    MathieuGrid** grid_out
);

MathieuStatus mathieu_grid_compute(
    double q_min, double q_max,
    double a_min, double a_max,
    const MathieuConfig* config,
    MathieuGrid* grid
);

void mathieu_grid_free(MathieuGrid* grid);

/* Спектральні показники та коефіцієнти Фур'є */
MathieuStatus mathieu_floquet_exponent(
    double a, double q,
    const MathieuConfig* config,
    double* mu_out, double* nu_out
);

MathieuStatus mathieu_fourier_coefficients(
    int order_n, double q,
    double* coeffs_out, size_t max_coeffs
);
