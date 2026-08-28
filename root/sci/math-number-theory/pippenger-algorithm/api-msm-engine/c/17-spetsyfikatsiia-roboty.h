/**
 * Виділення неперервного масиву точок з використанням Hugepages (2 МБ сторінки).
 * @param count Кількість точок базису.
 * @return Вказівник на вирівняну пам'ять або NULL у разі відсутності прав на Hugepages.
 */
msm_point_affine_t* msm_alloc_hugepages_points(size_t count);

/**
 * Звільнення пам'яті Hugepages.
 */
void msm_free_hugepages_points(msm_point_affine_t *ptr, size_t count);
