struct Stat { double spread, contrast, dmin, dmax; };

Stat measure(int n, int d, int queries, uint64_t seed) {
    const std::vector<double> base = gen(n, d, seed);
    const std::vector<double> qs   = gen(queries, d, seed + 0x51ED);
    const double* B = base.data();

    // 1) відносний розкид — по вибірці пар, за Велфордом
    Rng pick{seed + 0x9A17};
    const int m = 4000;
    double mean = 0.0, m2 = 0.0;
    for (int k = 1; k <= m; ++k) {
        const int i = static_cast<int>(pick.next() % static_cast<uint64_t>(n));
        int       j = static_cast<int>(pick.next() % static_cast<uint64_t>(n));
        if (j == i) j = (j + 1) % n;
        const double D = std::sqrt(dist2(B + static_cast<size_t>(i) * d,
                                         B + static_cast<size_t>(j) * d, d));
        const double delta = D - mean;
        mean += delta / k;
        m2   += delta * (D - mean);
    }
    const double spread = std::sqrt(m2 / m) / mean;

    // 2) контраст кожного запиту
    std::vector<double> cs(queries);
    double sdmin = 0.0, sdmax = 0.0;
    for (int q = 0; q < queries; ++q) {
        const double* Q = qs.data() + static_cast<size_t>(q) * d;
        double lo = HUGE_VAL, hi = 0.0;
        for (int i = 0; i < n; ++i) {
            const double D2 = dist2(Q, B + static_cast<size_t>(i) * d, d);
            if (D2 < lo) lo = D2;
            if (D2 > hi) hi = D2;
        }
        lo = std::sqrt(lo);  hi = std::sqrt(hi);   // корінь двічі на запит, а не n разів
        cs[q] = (hi - lo) / lo;
        sdmin += lo;  sdmax += hi;
    }
    std::nth_element(cs.begin(), cs.begin() + queries / 2, cs.end());
    return Stat{spread, cs[queries / 2], sdmin / queries, sdmax / queries};
}

int main() {
    std::printf("   d      s/m   contrast    D_min    D_max   0.59/sqrt(d)\n");
    for (int d : {2, 3, 10, 100, 1000}) {
        const Stat s = measure(1000, d, 101, 20260808ULL + d);
        std::printf("%4d   %6.3f   %8.2f  %7.3f  %7.3f   %8.3f\n",
                    d, s.spread, s.contrast, s.dmin, s.dmax,
                    0.59 / std::sqrt(static_cast<double>(d)));
    }
}
