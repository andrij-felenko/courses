namespace msm {

/* Побудова гістограми та сортування індексів за кошиками */
std::vector<uint32_t> sort_points_by_bucket(
    std::span<const FieldElement> scalars,
    uint32_t window_idx,
    uint32_t c,
    std::vector<uint32_t>& bucket_offsets
) {
    const size_t n = scalars.size();
    const size_t num_buckets = 1ULL << c;
    bucket_offsets.assign(num_buckets + 1, 0);

    /* 1. Підрахунок частот появи коефіцієнтів */
    for (size_t i = 0; i < n; ++i) {
        const uint32_t digit = extract_window(scalars[i], window_idx, c);
        bucket_offsets[digit + 1]++;
    }

    /* 2. Обчислення префіксних сум зміщень */
    for (size_t k = 1; k < num_buckets; ++k) {
        bucket_offsets[k + 1] += bucket_offsets[k];
    }

    /* 3. Розподіл індексів точок у суміжні кластери */
    std::vector<uint32_t> cur_pos = bucket_offsets;
    std::vector<uint32_t> sorted_indices(n);

    for (size_t i = 0; i < n; ++i) {
        const uint32_t digit = extract_window(scalars[i], window_idx, c);
        const uint32_t dst = cur_pos[digit]++;
        sorted_indices[dst] = static_cast<uint32_t>(i);
    }

    return sorted_indices;
}

} // namespace msm
