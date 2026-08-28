namespace msm {

/* Наївне послідовне обчислення MSM для перевірки коректності */
PointJacobian msm_naive_reference(
    std::span<const PointAffine> points,
    std::span<const FieldElement> scalars
) {
    PointJacobian result = PointJacobian::infinity();
    const size_t n = points.size();

    for (size_t i = 0; i < n; ++i) {
        PointJacobian p_acc = PointJacobian::infinity();
        for (int32_t b = 255; b >= 0; --b) {
            p_acc = double_point(p_acc);
            const uint32_t word = b / 64;
            const uint32_t bit = b % 64;
            if ((scalars[i].d[word] >> bit) & 1ULL) {
                p_acc = add_mixed(p_acc, points[i]);
            }
        }
        result = add_jacobian(result, p_acc);
    }
    return result;
}

/* Запуск вимірювань продуктивності */
void benchmark_msm_pipeline(size_t n) {
    std::vector<PointAffine> points(n);
    std::vector<FieldElement> scalars(n);

    for (size_t i = 0; i < n; ++i) {
        scalars[i].d[0] = static_cast<uint64_t>(i) * 0xdeadbeefULL + 17;
        scalars[i].d[1] = 0x12345678ULL;
        scalars[i].d[2] = 0;
        scalars[i].d[3] = 0;
        points[i].is_infinity = false;
        points[i].x = FieldElement{{1, 0, 0, 0}};
        points[i].y = FieldElement{{1, 0, 0, 0}};
    }

    const auto start = std::chrono::high_resolution_clock::now();
    PointJacobian res = msm_pippenger(points, scalars);
    const auto finish = std::chrono::high_resolution_clock::now();

    const auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(finish - start).count();
    (void)duration;
}

} // namespace msm
