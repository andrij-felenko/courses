void SuffixIndex::build_lcp() {
    int h = 0;
    for (int i = 0; i < n_; ++i) {
        if (rank_[i] > 0) {
            int j = sa_[rank_[i] - 1];
            while (i + h < n_ && j + h < n_ && text_[i + h] == text_[j + h]) {
                ++h;
            }
            lcp_[rank_[i]] = h;
            if (h > 0) --h;
        } else {
            lcp_[0] = 0;
        }
    }
}

void SuffixIndex::build_sparse_table() {
    int max_log = 0;
    while ((1 << max_log) <= n_) ++max_log;

    st_.assign(max_log, std::vector<int>(n_, 0));
    st_[0] = lcp_;

    for (int k = 1; k < max_log; ++k) {
        int span = 1 << (k - 1);
        for (int i = 0; i + (1 << k) <= n_; ++i) {
            st_[k][i] = std::min(st_[k - 1][i], st_[k - 1][i + span]);
        }
    }
}

int SuffixIndex::query_lcp(int sa_a, int sa_b) const noexcept {
    if (sa_a == sa_b) return n_ - sa_[sa_a];
    if (sa_a > sa_b) std::swap(sa_a, sa_b);

    int l = sa_a + 1;
    int r = sa_b;
    int len = r - l + 1;
    int k = 31 - __builtin_clz(static_cast<unsigned int>(len));
    return std::min(st_[k][l], st_[k][r - (1 << k) + 1]);
}
