#include <vector>
#include <string_view>
#include <span>

std::vector<int> build_lcp_kasai(std::string_view text, 
                                 std::span<const int> sa, 
                                 std::span<const int> rank) {
    const int n = static_cast<int>(text.size());
    std::vector<int> lcp(n, 0);

    int h = 0;
    for (int i = 0; i < n; ++i) {
        if (rank[i] > 0) {
            int j = sa[rank[i] - 1];
            while (i + h < n && j + h < n && text[i + h] == text[j + h]) {
                ++h;
            }
            lcp[rank[i]] = h;
            if (h > 0) --h;
        } else {
            lcp[0] = 0;
        }
    }

    return lcp;
}
