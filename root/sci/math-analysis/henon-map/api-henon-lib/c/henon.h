/* C99: Оголошення інтерфейсних функцій у henon.h */

/* Отримання замовчуваних параметрів a=1.4, b=0.3 */
henon_params_t henon_default_params(void);

/* Один крок прямого відображення (x[n], y[n]) -> (x[n+1], y[n+1]) */
henon_point_t henon_step(henon_point_t current, henon_params_t params);

/* Один крок оберненого відображення (x[n+1], y[n+1]) -> (x[n], y[n]) */
henon_status_t henon_step_inverse(henon_point_t next, henon_params_t params, henon_point_t *prev);

/* Серійна генерація точок орбіти з відсіканням транзієнту */
henon_status_t henon_iterate_batch(
    henon_point_t start,
    henon_params_t params,
    size_t transient,
    size_t count,
    henon_point_t *out_buffer
);

/* Обчислення спектра Ляпунова та розмірності Каплана-Йорка */
henon_status_t henon_compute_lyapunov(
    henon_point_t start,
    henon_params_t params,
    size_t transient,
    size_t steps,
    henon_lyapunov_t *out_lyap
);

/* Аналітичне знаходження двох нерухомих точок */
henon_fixed_points_t henon_find_fixed_points(henon_params_t params);
