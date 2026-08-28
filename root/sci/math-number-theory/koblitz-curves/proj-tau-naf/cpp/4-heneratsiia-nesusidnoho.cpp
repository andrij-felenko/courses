namespace koblitz {

struct ZTauElement {
    int64_t r0{0};
    int64_t r1{0};
};

/* Генерація канонічного розкладу TNAF за алгоритмом Солінаса */
[[nodiscard]] std::vector<int8_t> generate_tnaf(ZTauElement rho, int8_t mu) {
    std::vector<int8_t> tnaf;
    tnaf.reserve(MaxTnafLen);

    int64_t r0 = rho.r0;
    int64_t r1 = rho.r1;

    while (r0 != 0 || r1 != 0) {
        if (r0 & 1) {
            int64_t val = (r0 - 2 * r1 * mu) % 4;
            if (val < 0) val += 4;
            auto u = static_cast<int8_t>(2 - val);
            if (u != 1 && u != -1) {
                u = (val == 3) ? -1 : 1;
            }
            r0 -= u;
            tnaf.push_back(u);
        } else {
            tnaf.push_back(0);
        }

        const int64_t half_r0 = r0 / 2;
        const int64_t next_r0 = r1 + mu * half_r0;
        const int64_t next_r1 = -half_r0;

        r0 = next_r0;
        r1 = next_r1;
    }
    return tnaf;
}

} // namespace koblitz
