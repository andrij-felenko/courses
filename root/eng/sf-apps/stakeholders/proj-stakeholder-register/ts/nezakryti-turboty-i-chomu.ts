interface Gap { who: string; concern: Attribute; veto: boolean; score: number; }

function coverageGaps(reg: Stakeholder[], decisions: Decision[]): Gap[] {
  const covered = new Set(decisions.map(d => d.closes));   // що архітектура вже закрила
  return reg
    .filter(s => !covered.has(s.concern))                  // чия турбота лишилась без відповіді
    .map(s => ({ who: s.name, concern: s.concern, veto: !!s.hard, score: salienceScore(s) }))
    // спершу тверді вето, тоді — за кількістю осей вагомості
    .sort((a, b) => Number(b.veto) - Number(a.veto) || b.score - a.score);
}
