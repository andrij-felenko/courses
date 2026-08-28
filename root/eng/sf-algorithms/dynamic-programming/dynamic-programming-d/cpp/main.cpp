#include <vector>
#include <optional>

std::optional<std::vector<int>> min_coins(const std::vector<int>& coins, int amount) {
    const int INF = amount + 1;
    std::vector<int> dp(amount + 1, INF), from(amount + 1, -1);
    dp[0] = 0;                                   // база
    for (int a = 1; a <= amount; ++a)
        for (int c : coins)
            if (c <= a && dp[a - c] + 1 < dp[a]) {
                dp[a]   = dp[a - c] + 1;         // кращий перехід
                from[a] = c;                     // запам'ятати вибір для відновлення
            }
    if (dp[amount] >= INF) return std::nullopt;  // недосяжно
    std::vector<int> used;
    for (int a = amount; a > 0; a -= from[a])    // йдемо від цілі назад
        used.push_back(from[a]);
    return used;
}
