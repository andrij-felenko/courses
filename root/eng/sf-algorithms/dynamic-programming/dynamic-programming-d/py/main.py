def min_coins(coins, amount):
    INF = amount + 1
    dp   = [0] + [INF] * amount        # dp[0] = 0, решта — «поки недосяжно»
    frm  = [-1] * (amount + 1)         # яка монета дала мінімум для суми a
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a]  = dp[a - c] + 1
                frm[a] = c
    if dp[amount] >= INF:
        return None                    # такими монетами суму не набрати
    coins_used, a = [], amount         # відновлюємо розв'язок, ідучи назад
    while a > 0:
        coins_used.append(frm[a])
        a -= frm[a]
    return coins_used
