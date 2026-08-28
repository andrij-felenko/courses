// "Оптимізовано" наосліп: ручне розгортання по 4. Поділ у тілі — НЕ ЧІПАЄМО,
// бо око його не помітило. Читати важче, з'явився окремий "хвіст", межу n
// треба обробляти руками — новий шанс на баг саме тут.
float compute_rms_mA_unrolled(const uint16_t *raw, size_t n) {
    uint64_t sum_sq = 0;
    size_t i = 0;
    for (; i + 4 <= n; i += 4) {
        int32_t c0 = (int32_t)raw[i]   - g_offset;
        int32_t c1 = (int32_t)raw[i+1] - g_offset;
        int32_t c2 = (int32_t)raw[i+2] - g_offset;
        int32_t c3 = (int32_t)raw[i+3] - g_offset;
        int32_t m0 = c0 * g_scale_num / g_scale_den;   // ← поділ ЛИШИВСЯ
        int32_t m1 = c1 * g_scale_num / g_scale_den;   // ← і тут
        int32_t m2 = c2 * g_scale_num / g_scale_den;   // ← і тут
        int32_t m3 = c3 * g_scale_num / g_scale_den;   // ← і тут
        sum_sq += (uint64_t)((int64_t)m0*m0) + (uint64_t)((int64_t)m1*m1)
                + (uint64_t)((int64_t)m2*m2) + (uint64_t)((int64_t)m3*m3);
    }
    for (; i < n; i++) {                                // окремий хвіст — новий баг-ризик
        int32_t c = (int32_t)raw[i] - g_offset;
        int32_t m = c * g_scale_num / g_scale_den;
        sum_sq += (uint64_t)((int64_t)m * m);
    }
    float mean_sq = (float)sum_sq / (float)n;
    return sqrtf(mean_sq);
}
