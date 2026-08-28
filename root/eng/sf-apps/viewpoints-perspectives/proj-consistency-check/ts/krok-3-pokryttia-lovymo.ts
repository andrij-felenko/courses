interface Orphan { element: string; missing: View[]; }

function checkCoverage(groups: Manifestation[][], required: View[]): Orphan[] {
  const orphans: Orphan[] = [];
  for (const group of groups) {
    const fe = group.find(m => m.view === 'functional');
    if (!fe) continue;                                   // група без функц. елемента — не тут
    const views = new Set(group.map(m => m.view));
    const missing = required.filter(v => !views.has(v)); // ← обхід required × ця група
    if (missing.length) orphans.push({ element: fe.label, missing });
  }
  return orphans;
}
