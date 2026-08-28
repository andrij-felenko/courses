function knapsackPick(strategies: Strategy[], budget: number) {
  // Точний 0/1-наплічник. Вартості й бюджет — цілі (тижні). O(n·B) час і пам'ять.
  const n = strategies.length;
  const B = Math.floor(budget);
  const cost = strategies.map((s) => Math.floor(s.cost));
  const value = strategies.map(benefit);

  // dp[i][b] — максимальна вигода з перших i стратегій за бюджету b.
  const dp: number[][] = Array.from({ length: n + 1 }, () => new Array(B + 1).fill(0));
  for (let i = 1; i <= n; i++) {
    const ci = cost[i - 1], vi = value[i - 1];
    for (let b = 0; b <= B; b++) {
      dp[i][b] = dp[i - 1][b];                     // не беремо i-ту
      if (ci <= b) {                               // або беремо, якщо влазить
        const take = dp[i - 1][b - ci] + vi;
        if (take > dp[i][b]) dp[i][b] = take;
      }
    }
  }

  // Відновлення набору: йдемо таблицею назад.
  const chosen: Strategy[] = [];
  let b = B;
  for (let i = n; i >= 1; i--) {
    if (dp[i][b] !== dp[i - 1][b]) {                // i-ту брали
      chosen.push(strategies[i - 1]);
      b -= cost[i - 1];
    }
  }
  chosen.reverse();
  return { chosen, spent: B - b, total: dp[n][B] };
}
