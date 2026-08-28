/**
 * @brief Знаходить ліву та праву межі язика Арнольда p/q при заданому K.
 * @param[in] k_val Амплітуда нелінійного зв'язку K.
 * @param[in] p Чисельник резонансу.
 * @param[in] q Знаменник резонансу.
 * @param[in] bisection_tol Точність пошуку межі.
 * @param[out] out_omega_left Ліва межа язика Omega_left.
 * @param[out] out_omega_right Права межа язика Omega_right.
 * @return Код статусу виконання circle_map_status_t.
 */
circle_map_status_t circle_map_find_tongue_boundaries(
    double k_val,
    int p,
    int q,
    double bisection_tol,
    double *out_omega_left,
    double *out_omega_right
);
