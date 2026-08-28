#include <string_view>
#include <vector>
#include <cmath>
#include <algorithm>
#include <limits>

int levenshtein_banded_ukkonen(std::string_view s1, std::string_view s2, int k) {
    const int n = static_cast<int>(s1.size());
    const int m = static_cast<int>(s2.size());

    if (std::abs(n - m) > k) {
        return k + 1;
    }

    constexpr int INF = std::numeric_limits<int>::max() / 2;
    std::vector<int> prev(m + 1, INF);
    std::vector<int> curr(m + 1, INF);

    for (int j = 0; j <= std::min(m, k); ++j) {
        prev[j] = j;
    }

    for (int i = 1; i <= n; ++i) {
        const int min_j = std::max(0, i - k);
        const int max_j = std::min(m, i + k);

        std::fill(curr.begin(), curr.end(), INF);
        if (min_j == 0) curr[0] = i;

        int row_min = curr[0];

        for (int j = std::max(1, min_j); j <= max_j; ++j) {
            const int cost = (s1[i - 1] == s2[j - 1]) ? 0 : 1;
            curr[j] = std::min({
                prev[j] + 1,
                curr[j - 1] + 1,
                prev[j - 1] + cost
            });
            row_min = std::min(row_min, curr[j]);
        }

        if (row_min > k) {
            return k + 1;
        }

        std::swap(prev, curr);
    }

    return (prev[m] <= k) ? prev[m] : (k + 1);
}
