def knapsack_pick(strategies: list[Strategy], budget: float):
    # Точний 0/1-наплічник. Вартості й бюджет — цілі (тижні). O(n·B) час і пам'ять.
    n, B = len(strategies), int(budget)
    cost = [int(s.cost) for s in strategies]
    value = [s.benefit() for s in strategies]

    # dp[i][b] — максимальна вигода з перших i стратегій за бюджету b.
    dp = [[0.0] * (B + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        ci, vi = cost[i - 1], value[i - 1]
        for b in range(B + 1):
            dp[i][b] = dp[i - 1][b]                     # не беремо i-ту
            if ci <= b:                                 # або беремо, якщо влазить
                take = dp[i - 1][b - ci] + vi
                if take > dp[i][b]:
                    dp[i][b] = take

    # Відновлення набору: йдемо таблицею назад.
    chosen, b = [], B
    for i in range(n, 0, -1):
        if dp[i][b] != dp[i - 1][b]:                    # i-ту брали
            chosen.append(strategies[i - 1])
            b -= cost[i - 1]
    chosen.reverse()
    return chosen, B - b, dp[n][B]
