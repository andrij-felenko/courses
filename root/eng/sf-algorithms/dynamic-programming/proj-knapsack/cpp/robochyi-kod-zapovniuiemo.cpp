#include <vector>
#include <algorithm>
using std::vector;

// Будує таблицю dp[i][w] і повертає її цілком.
// wt[k], val[k] — вага й цінність k-ї речі (k від 0); cap — місткість W.
vector<vector<int>> knap_table(const vector<int>& wt,
                               const vector<int>& val, int cap) {
    int n = (int)wt.size();
    vector<vector<int>> dp(n + 1, vector<int>(cap + 1, 0));   // рядок 0 — самі нулі
    for (int i = 1; i <= n; ++i)
        for (int w = 0; w <= cap; ++w) {
            dp[i][w] = dp[i - 1][w];                          // не брати i-ту річ
            if (wt[i - 1] <= w) {                             // якщо влазить —
                int take = dp[i - 1][w - wt[i - 1]] + val[i - 1];
                if (take > dp[i][w]) dp[i][w] = take;         // …спробувати взяти
            }
        }
    return dp;                                                // відповідь — dp[n][cap]
}
