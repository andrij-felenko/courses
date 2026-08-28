namespace msm {

/* Головна функція паралельного обчислення MSM за алгоритмом Піппенджера */
PointJacobian msm_pippenger(
    std::span<const PointAffine> points,
    std::span<const FieldElement> scalars
) {
    const size_t n = points.size();
    if (n == 0 || scalars.size() != n) {
        return PointJacobian::infinity();
    }

    /* Вибір оптимального розміру вікна c за розміром входу */
    uint32_t c = 16;
    if (n < 4096) c = 10;
    else if (n < 65536) c = 13;
    else if (n < 524288) c = 15;

    const uint32_t b = (256 + c - 1) / c;
    std::vector<PointJacobian> window_results(b, PointJacobian::infinity());
    std::vector<std::thread> workers;
    workers.reserve(b);

    /* Паралельний запуск обчислення вікон */
    for (uint32_t j = 0; j < b; ++j) {
        workers.emplace_back([&, j]() {
            window_results[j] = compute_window_sum(points, scalars, j, c);
        });
    }

    for (auto& t : workers) {
        if (t.joinable()) {
            t.join();
        }
    }

    /* Міжвіконна агрегація за Горнером: Q = [2^c]Q + S_j */
    PointJacobian acc = window_results[b - 1];
    for (int64_t j = static_cast<int64_t>(b) - 2; j >= 0; --j) {
        for (uint32_t step = 0; step < c; ++step) {
            acc = double_point(acc);
        }
        if (!window_results[j].is_infinity()) {
            acc = add_jacobian(acc, window_results[j]);
        }
    }

    return acc;
}

} // namespace msm
