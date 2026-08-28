typedef struct {
    double k_bifurcation;
    int period;
    double feigenbaum_delta;
} circle_map_bifurcation_point_t;

/**
 * @brief Знаходить точку наступної біфуркації подвоєння періоду.
 */
circle_map_status_t circle_map_find_bifurcation(
    double k_start,
    int current_period,
    circle_map_bifurcation_point_t *out_bif
);
