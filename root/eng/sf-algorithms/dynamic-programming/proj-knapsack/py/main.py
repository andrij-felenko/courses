def knap_table(wt, val, cap):
    n = len(wt)
    dp = [[0] * (cap + 1) for _ in range(n + 1)]      # рядок 0 — самі нулі
    for i in range(1, n + 1):
        for w in range(cap + 1):
            dp[i][w] = dp[i - 1][w]                    # не брати i-ту річ
            if wt[i - 1] <= w:                         # якщо влазить —
                take = dp[i - 1][w - wt[i - 1]] + val[i - 1]
                dp[i][w] = max(dp[i][w], take)         # …спробувати взяти
    return dp                                          # відповідь — dp[n][cap]
