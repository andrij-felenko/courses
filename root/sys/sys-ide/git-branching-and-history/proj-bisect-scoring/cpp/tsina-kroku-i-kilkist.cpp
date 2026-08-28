const int W = (N + 63) / 64;                 // слів на одну маску
std::vector<std::uint64_t> reach(static_cast<std::size_t>(N) * W, 0);

for (int i : order) {                        // order — той самий топологічний
                                             // порядок, побудований наперед
    std::uint64_t* row = &reach[static_cast<std::size_t>(i) * W];
    const int v = c.id[i];
    for (int k = g.par_off[v]; k < g.par_off[v + 1]; ++k) {
        const int j = c.local[g.par[k]];
        if (j < 0) continue;
        const std::uint64_t* prow = &reach[static_cast<std::size_t>(j) * W];
        for (int w = 0; w < W; ++w) row[w] |= prow[w];
    }
    row[i >> 6] |= std::uint64_t{1} << (i & 63);
    int cnt = 0;
    for (int w = 0; w < W; ++w) cnt += std::popcount(row[w]);
    a[i] = cnt;
}
