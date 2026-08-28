namespace msm {

/* Обчислення суми вікна j за алгоритмом Піппенджера */
PointJacobian compute_window_sum(
    std::span<const PointAffine> points,
    std::span<const FieldElement> scalars,
    uint32_t window_idx,
    uint32_t c
) {
    const size_t num_buckets = (1ULL << c) - 1;
    std::vector<PointJacobian> buckets(num_buckets, PointJacobian::infinity());

    /* 1. Розподіл точок по кошиках */
    const size_t n = points.size();
    for (size_t i = 0; i < n; ++i) {
        const uint32_t digit = extract_window(scalars[i], window_idx, c);
        if (digit > 0) {
            const size_t bucket_idx = digit - 1;
            buckets[bucket_idx] = add_mixed(buckets[bucket_idx], points[i]);
        }
    }

    /* 2. Зворотне накопичення Running Sums */
    PointJacobian running_sum = PointJacobian::infinity();
    PointJacobian window_sum = PointJacobian::infinity();

    for (int64_t v = static_cast<int64_t>(num_buckets) - 1; v >= 0; --v) {
        if (!buckets[v].is_infinity()) {
            running_sum = add_jacobian(running_sum, buckets[v]);
        }
        if (!running_sum.is_infinity()) {
            window_sum = add_jacobian(window_sum, running_sum);
        }
    }

    return window_sum;
}

} // namespace msm
