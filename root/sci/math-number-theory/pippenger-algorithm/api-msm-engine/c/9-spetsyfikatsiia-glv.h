/**
 * Розклад масиву 256-бітних скалярів на дві половини за алгоритмом Бабая.
 * @param k1_out  Вихідний масив перших половин скалярів (128 бітів).
 * @param k2_out  Вихідний масив других половин скалярів (128 бітів).
 * @param scalars Вхідний масив 256-бітних скалярів розміром n.
 * @param n       Кількість скалярів.
 * @param curve   Ідентифікатор кривої.
 */
msm_status_t msm_glv_decompose_scalars(
    msm_fe256_t *k1_out,
    msm_fe256_t *k2_out,
    const msm_fe256_t *scalars,
    size_t n,
    msm_curve_id_t curve
);

/**
 * Виконання MSM з використанням попередньо обчисленого ендоморфізму GLV.
 */
msm_status_t msm_glv_execute(
    msm_point_jacobian_t *result,
    const msm_point_affine_t *points,
    const msm_fe256_t *k1,
    const msm_fe256_t *k2,
    size_t n,
    const msm_config_t *config
);
