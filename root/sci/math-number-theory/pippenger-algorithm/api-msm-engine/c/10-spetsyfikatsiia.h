/* Контекст попередньо обчисленої таблиці фіксованого базису */
typedef struct msm_fixed_base_table msm_fixed_base_table_t;

/**
 * Створення таблиці попередніх обчислень для фіксованого набору точок.
 * @param points Масив точок базису розміром n.
 * @param n      Розмір базису.
 * @param window_size Ширина вікна попередніх обчислень (наприклад, 4 або 8 бітів).
 * @param curve  Ідентифікатор кривої.
 */
msm_fixed_base_table_t* msm_fixed_base_table_create(
    const msm_point_affine_t *points,
    size_t n,
    uint32_t window_size,
    msm_curve_id_t curve
);

/**
 * Прискорене обчислення MSM над фіксованим базисом.
 */
msm_status_t msm_fixed_base_execute(
    msm_point_jacobian_t *result,
    const msm_fixed_base_table_t *table,
    const msm_fe256_t *scalars,
    size_t n
);

/**
 * Звільнення пам'яті таблиці фіксованого базису.
 */
void msm_fixed_base_table_destroy(msm_fixed_base_table_t *table);
