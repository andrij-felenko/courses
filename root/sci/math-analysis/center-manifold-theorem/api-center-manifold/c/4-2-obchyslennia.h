/* Обчислює тензори коефіцієнтів h(x) до вказаного порядку order */
cm_status_e cm_compute_manifold(
    const cm_system_t       *sys,
    const cm_solver_config_t *config,
    cm_manifold_t          **manifold
);

/* Обчислює векторне значення h(x) у заданій фазовій точці x */
cm_status_e cm_eval_manifold(
    const cm_manifold_t *manifold,
    const double        *x,
    double              *out_y
);

/* Звільняє пам'ять тензора коефіцієнтів многовиду */
void cm_manifold_destroy(cm_manifold_t *manifold);
