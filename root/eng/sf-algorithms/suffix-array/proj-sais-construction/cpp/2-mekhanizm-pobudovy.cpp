void SuffixIndex::build_sa() {
    std::vector<int> temp_sa(n_);
    std::vector<int> cnt;
    std::vector<int> new_rank(n_);

    // 1. Початкова ініціалізація символьними кодами
    for (int i = 0; i < n_; ++i) {
        sa_[i] = i;
        rank_[i] = static_cast<unsigned char>(text_[i]);
    }

    // 2. Ітерації подвоєння префіксів: k = 1, 2, 4, 8...
    for (int k = 1; k < n_; k <<= 1) {
        auto count_sort_pass = [&](int offset) {
            int max_val = 0;
            for (int i = 0; i < n_; ++i) {
                int val = (i + offset < n_) ? rank_[i + offset] + 1 : 0;
                if (val > max_val) max_val = val;
            }
            cnt.assign(max_val + 2, 0);

            for (int i = 0; i < n_; ++i) {
                int val = (i + offset < n_) ? rank_[i + offset] + 1 : 0;
                cnt[val]++;
            }
            for (size_t i = 1; i < cnt.size(); ++i) {
                cnt[i] += cnt[i - 1];
            }
            for (int i = n_ - 1; i >= 0; --i) {
                int val = (sa_[i] + offset < n_) ? rank_[sa_[i] + offset] + 1 : 0;
                temp_sa[--cnt[val]] = sa_[i];
            }
            sa_ = temp_sa;
        };

        // Двопрохідне сортування за парою (rank[i], rank[i + k])
        count_sort_pass(k);
        count_sort_pass(0);

        // Оновлення масиву рангів
        new_rank[sa_[0]] = 0;
        int r = 0;
        for (int i = 1; i < n_; ++i) {
            int prev = sa_[i - 1];
            int curr = sa_[i];
            int prev_r2 = (prev + k < n_) ? rank_[prev + k] : -1;
            int curr_r2 = (curr + k < n_) ? rank_[curr + k] : -1;

            if (rank_[prev] != rank_[curr] || prev_r2 != curr_r2) {
                ++r;
            }
            new_rank[curr] = r;
        }
        rank_ = new_rank;
        if (r == n_ - 1) break; // Ранги всіх суфіксів стали унікальними
    }
}
