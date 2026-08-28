/**
 * Одночасне обчислення K незалежних мультискалярних множень над спільним базисом точок.
 * @param results    Масив із K вихідних точок у координатах Якобі.
 * @param points     Спільний масив із n афінних точок базису.
 * @param scalars_2d Двовимірний масив скалярів розміром K * n.
 * @param n          Кількість точок у базисі.
 * @param batch_size Кількість незалежних задач K.
 * @param config     Параметри конфігурації.
 */
msm_status_t msm_execute_batched(
    msm_point_jacobian_t *results,
    const msm_point_affine_t *points,
    const msm_fe256_t *scalars_2d,
    size_t n,
    size_t batch_size,
    const msm_config_t *config
);
