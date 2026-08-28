typedef struct {
    size_t num_oscillators;
    const double *omegas;
    double k_global;
    double coupling_g;
} circle_map_coupled_config_t;

/**
 * @brief Обчислює вектор чисел обертання для ансамблю осциляторів.
 */
circle_map_status_t circle_map_solve_coupled(
    const circle_map_coupled_config_t *cfg,
    size_t steps,
    double *out_rotations
);
