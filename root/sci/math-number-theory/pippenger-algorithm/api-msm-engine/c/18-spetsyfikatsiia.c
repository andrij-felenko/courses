/**
 * Валідація результату MSM проти наївного еталонного оракула.
 * @return true, якщо координати точок повністю збігаються після приведення до афінної форми.
 */
bool msm_oracle_verify(
    const msm_point_jacobian_t *result,
    const msm_point_affine_t *points,
    const msm_fe256_t *scalars,
    size_t n,
    msm_curve_id_t curve
);
