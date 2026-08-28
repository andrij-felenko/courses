#include <vector>
#include <algorithm>

// Точний 0/1-наплічник. Вартості й бюджет — цілі (тижні). O(n·B) час і пам'ять.
Pick knapsack_pick(const std::vector<Strategy>& strategies, double budget) {
    const int n = static_cast<int>(strategies.size());
    const int B = static_cast<int>(budget);

    std::vector<int> cost(n);
    std::vector<double> value(n);
    for (int i = 0; i < n; ++i) {
        cost[i]  = static_cast<int>(strategies[i].cost);
        value[i] = strategies[i].benefit();
    }

    // dp[i][b] — максимальна вигода з перших i стратегій за бюджету b.
    std::vector<std::vector<double>> dp(n + 1, std::vector<double>(B + 1, 0.0));
    for (int i = 1; i <= n; ++i) {
        const int ci = cost[i - 1];
        const double vi = value[i - 1];
        for (int b = 0; b <= B; ++b) {
            dp[i][b] = dp[i - 1][b];                 // не беремо i-ту
            if (ci <= b) {                           // або беремо, якщо влазить
                double take = dp[i - 1][b - ci] + vi;
                if (take > dp[i][b]) dp[i][b] = take;
            }
        }
    }

    // Відновлення набору: йдемо таблицею назад.
    Pick p{{}, 0.0, dp[n][B]};
    int b = B;
    for (int i = n; i >= 1; --i) {
        if (dp[i][b] != dp[i - 1][b]) {              // i-ту брали
            p.chosen.push_back(strategies[i - 1]);
            b -= cost[i - 1];
        }
    }
    std::reverse(p.chosen.begin(), p.chosen.end());
    p.spent = static_cast<double>(B - b);
    return p;
}
