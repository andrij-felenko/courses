function rankByRoi(strategies: Strategy[]): Strategy[] {
  // Перший зріз: за ROI спадно. O(n log n).
  return [...strategies].sort((a, b) => roi(b) - roi(a));
}

function greedyPick(strategies: Strategy[], budget: number) {
  // Іди по ранжованому списку й бери все, що ще влазить у бюджет.
  const chosen: Strategy[] = [];
  let spent = 0;
  for (const s of rankByRoi(strategies)) {
    if (spent + s.cost <= budget) {
      chosen.push(s);
      spent += s.cost;
    }
  }
  const total = chosen.reduce((acc, s) => acc + benefit(s), 0);
  return { chosen, spent, total };
}
