/**
 * @brief Сканує двовимірну сітку параметрів (Omega, K).
 * @param[in] base_cfg Кількість ітерацій та початкові умови.
 * @param[in] omega_min Нижнє значення Omega.
 * @param[in] omega_max Верхнє значення Omega.
 * @param[in] res_omega Роздільна здатність по осі Omega.
 * @param[in] k_min Нижнє значення K.
 * @param[in] k_max Верхнє значення K.
 * @param[in] res_k Роздільна здатність по осі K.
 * @param[out] out_w_matrix Вихідний масив чисел обертання (розмір res_w * res_k).
 * @param[out] out_locked_matrix Вихідний масив статусу захоплення (розмір res_w * res_k).
 * @return Код статусу виконання circle_map_status_t.
 */
circle_map_status_t circle_map_scan_grid(
    const circle_map_config_t *base_cfg,
    double omega_min, double omega_max, size_t res_omega,
    double k_min, double k_max, size_t res_k,
    double *out_w_matrix,
    bool *out_locked_matrix
);
