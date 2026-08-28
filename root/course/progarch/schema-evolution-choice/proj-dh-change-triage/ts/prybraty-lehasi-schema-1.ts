interface RetireGate {
  version: number;
  liveWrites: number;                  // писарі, що ще шлють цю версію (за вікно)
  oldestStoredAgeDays: number | null;  // вік найстарішого збереженого рядка; null = жодного
  retentionDays: number;               // доки взагалі можемо перечитувати історію
}

function canRetireDecoder(g: RetireGate): { green: boolean; why: string } {
  if (g.liveWrites > 0)
    return { green: false, why: `${g.liveWrites} писарів ще шлють schema:${g.version}` };
  if (g.oldestStoredAgeDays !== null && g.oldestStoredAgeDays <= g.retentionDays)
    return { green: false,
      why: `найстаріший schema:${g.version}-рядок ще в retention — перерахунок його прочитає` };
  return { green: true, why: `ні писаря, ні досяжного рядка на schema:${g.version}` };
}
