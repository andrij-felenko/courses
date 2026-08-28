/* Обчислює вектор правого боку редукованої системи: dx/dt = A*x + f(x, h(x)) */
cm_status_e cm_eval_reduced_rhs(
    const cm_system_t   *sys,
    const cm_manifold_t *manifold,
    const double        *x,
    double              *out_dxdt
);

/* Виконує один крок чисельного інтегрування редукованої системи методом RK4 */
cm_status_e cm_step_reduced_rk4(
    const cm_system_t   *sys,
    const cm_manifold_t *manifold,
    double              *inout_x,
    double               dt
);
