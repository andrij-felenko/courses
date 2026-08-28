#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <algorithm>

struct AlignmentResult {
    int distance = 0;
    std::string aligned_s1;
    std::string aligned_s2;
    std::string cigar;
};

AlignmentResult align_levenshtein(std::string_view s1, std::string_view s2) {
    const size_t n = s1.size();
    const size_t m = s2.size();

    std::vector<std::vector<int>> dp(n + 1, std::vector<int>(m + 1, 0));

    for (size_t i = 0; i <= n; ++i) dp[i][0] = static_cast<int>(i);
    for (size_t j = 0; j <= m; ++j) dp[0][j] = static_cast<int>(j);

    for (size_t i = 1; i <= n; ++i) {
        for (size_t j = 1; j <= m; ++j) {
            const int cost = (s1[i - 1] == s2[j - 1]) ? 0 : 1;
            dp[i][j] = std::min({
                dp[i - 1][j] + 1,        // видалення
                dp[i][j - 1] + 1,        // вставка
                dp[i - 1][j - 1] + cost  // заміна або збіг
            });
        }
    }

    AlignmentResult res;
    res.distance = dp[n][m];

    size_t ci = n, cj = m;
    while (ci > 0 || cj > 0) {
        if (ci > 0 && cj > 0 && dp[ci][cj] == dp[ci - 1][cj - 1] + (s1[ci - 1] == s2[cj - 1] ? 0 : 1)) {
            res.aligned_s1.push_back(s1[ci - 1]);
            res.aligned_s2.push_back(s2[cj - 1]);
            res.cigar.push_back(s1[ci - 1] == s2[cj - 1] ? 'M' : 'S');
            --ci; --cj;
        } else if (ci > 0 && dp[ci][cj] == dp[ci - 1][cj] + 1) {
            res.aligned_s1.push_back(s1[ci - 1]);
            res.aligned_s2.push_back('-');
            res.cigar.push_back('D');
            --ci;
        } else {
            res.aligned_s1.push_back('-');
            res.aligned_s2.push_back(s2[cj - 1]);
            res.cigar.push_back('I');
            --cj;
        }
    }

    std::reverse(res.aligned_s1.begin(), res.aligned_s1.end());
    std::reverse(res.aligned_s2.begin(), res.aligned_s2.end());
    std::reverse(res.cigar.begin(), res.cigar.end());

    return res;
}
