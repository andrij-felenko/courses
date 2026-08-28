/* Структура для індексованого пакетного доступу до кошиків */
typedef struct {
    uint32_t point_idx;
    uint32_t bucket_idx;
} bucket_entry_t;

/* Побудова гістограми та сортування індексів за кошиками */
void sort_points_by_bucket(
    uint32_t *sorted_indices,
    uint32_t *bucket_offsets,
    const fe256_t *scalars,
    size_t n,
    uint32_t window_idx,
    uint32_t c
) {
    uint32_t num_buckets = 1U << c;
    memset(bucket_offsets, 0, (num_buckets + 1) * sizeof(uint32_t));

    /* 1. Підрахунок кількості точок у кожному кошику */
    for (size_t i = 0; i < n; ++i) {
        uint32_t digit = extract_window(&scalars[i], window_idx, c);
        bucket_offsets[digit + 1]++;
    }

    /* 2. Обчислення префіксних сум для зміщень */
    for (uint32_t k = 1; k < num_buckets; ++k) {
        bucket_offsets[k + 1] += bucket_offsets[k];
    }

    /* 3. Розподіл індексів точок по відсортованих позиціях */
    uint32_t *cur_pos = (uint32_t*)malloc(num_buckets * sizeof(uint32_t));
    memcpy(cur_pos, bucket_offsets, num_buckets * sizeof(uint32_t));

    for (size_t i = 0; i < n; ++i) {
        uint32_t digit = extract_window(&scalars[i], window_idx, c);
        uint32_t dst = cur_pos[digit]++;
        sorted_indices[dst] = (uint32_t)i;
    }

    free(cur_pos);
}
