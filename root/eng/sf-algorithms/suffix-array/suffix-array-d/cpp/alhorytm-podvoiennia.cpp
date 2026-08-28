#include <vector>
#include <string_view>
#include <numeric>
#include <algorithm>

std::vector<int> build_suffix_array(std::string_view text) {
    const int n = static_cast<int>(text.size());
    if (n == 0) return {};

    std::vector<int> sa(n);
    std::vector<int> rank(n);
    std::vector<int> temp_sa(n);
    std::vector<int> new_rank(n);
    std::vector<int> cnt;

    for (int i = 0; i < n; ++i) {
        sa[i] = i;
        rank[i] = static_cast<unsigned char>(text[i]);
    }

    for (int k = 1; k < n; k <<= 1) {
        auto counting_pass = [&](int offset) {
            int max_val = 0;
            for (int i = 0; i < n; ++i) {
                int val = (i + offset < n) ? rank[i + offset] + 1 : 0;
                if (val > max_val) max_val = val;
            }
            cnt.assign(max_val + 2, 0);

            for (int i = 0; i < n; ++i) {
                int val = (i + offset < n) ? rank[i + offset] + 1 : 0;
                cnt[val]++;
            }
            for (size_t i = 1; i < cnt.size(); ++i) {
                cnt[i] += cnt[i - 1];
            }
            for (int i = n - 1; i >= 0; --i) {
                int val = (sa[i] + offset < n) ? rank[sa[i] + offset] + 1 : 0;
                temp_sa[--cnt[val]] = sa[i];
            }
            sa = temp_sa;
        };

        counting_pass(k);
        counting_pass(0);

        new_rank[sa[0]] = 0;
        int r = 0;
        for (int i = 1; i < n; ++i) {
            int prev = sa[i - 1];
            int curr = sa[i];
            int prev_r2 = (prev + k < n) ? rank[prev + k] : -1;
            int curr_r2 = (curr + k < n) ? rank[curr + k] : -1;
            if (rank[prev] != rank[curr] || prev_r2 != curr_r2) {
                ++r;
            }
            new_rank[curr] = r;
        }
        rank = new_rank;
        if (r == n - 1) break;
    }

    return sa;
}
