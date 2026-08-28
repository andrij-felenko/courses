#include <string_view>
#include <vector>
#include <algorithm>

int levenshtein_distance_fast(std::string_view s1, std::string_view s2) {
    if (s1.size() < s2.size()) {
        std::swap(s1, s2);
    }

    const size_t n = s1.size();
    const size_t m = s2.size();

    std::vector<int> dp(m + 1);
    for (size_t j = 0; j <= m; ++j) {
        dp[j] = static_cast<int>(j);
    }

    for (size_t i = 1; i <= n; ++i) {
        int diag = dp[0];
        dp[0] = static_cast<int>(i);
        const char c1 = s1[i - 1];

        for (size_t j = 1; j <= m; ++j) {
            const int temp = dp[j];
            const int cost = (c1 == s2[j - 1]) ? 0 : 1;

            dp[j] = std::min({
                dp[j] + 1,       // видалення
                dp[j - 1] + 1,   // вставка
                diag + cost      // заміна або збіг
            });

            diag = temp;
        }
    }

    return dp[m];
}
