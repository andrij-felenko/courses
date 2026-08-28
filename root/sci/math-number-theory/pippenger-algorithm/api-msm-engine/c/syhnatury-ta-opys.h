/**
 * Ініціалізація структури конфігурації значеннями за замовчуванням.
 * @param config Вказівник на структуру конфігурації.
 * @param curve  Ідентифікатор еліптичної кривої.
 */
void msm_config_init_default(msm_config_t *config, msm_curve_id_t curve);

/**
 * Розрахунок мінімального обсягу пам'яті арени для обробки n точок.
 * @param config Вказівник на конфігурацію.
 * @param n      Кількість вхідних точок.
 * @return Необхідний розмір буфера у байтах.
 */
size_t msm_calculate_arena_size(const msm_config_t *config, size_t n);

/**
 * Головна функція обчислення мультискалярного множення:
 * result = sum_{i=0}^{n-1} scalars[i] * points[i]
 *
 * @param result  Вказівник на вихідну точку в координатах Якобі.
 * @param points  Масив вхідних афінних точок базису розміром n.
 * @param scalars Масив 256-бітних скалярів розміром n.
 * @param n       Кількість пар (точка, скаляр).
 * @param config  Вказівник на параметри запуску (може бути NULL для дефолтних налаштувань).
 * @return Статус виконання (MSM_SUCCESS у разі успіху).
 */
msm_status_t msm_execute(
    msm_point_jacobian_t *result,
    const msm_point_affine_t *points,
    const msm_fe256_t *scalars,
    size_t n,
    const msm_config_t *config
);

/**
 * Пакетна конвертація масиву точок з координат Якобі в афінні координати
 * з використанням алгоритму Монтгомері (одна інверсія в полі).
 *
 * @param out_affine  Масив вихідних афінних точок розміром count.
 * @param in_jacobian Масив вхідних проективних точок розміром count.
 * @param count       Кількість конвертованих точок.
 * @param curve       Ідентифікатор кривої.
 * @return Статус виконання.
 */
msm_status_t msm_batch_to_affine(
    msm_point_affine_t *out_affine,
    const msm_point_jacobian_t *in_jacobian,
    size_t count,
    msm_curve_id_t curve
);
