const N = 3, W = 2, R = 2;               // R + W = 4 > N = 3 → кворуми ПЕРЕТИНАЮТЬСЯ

class NoQuorum extends Error {}

// СТРОГО: опитати R копій і взяти НАЙСВІЖІШУ версію серед них. Перетин кворумів
// гарантує, що серед прочитаних є копія з останнім підтвердженим записом.
function readStrong(key: string, reachable: Replica[]): Rec | undefined {
  if (reachable.length < R)
    throw new NoQuorum(`строге читання: доступно ${reachable.length} < R=${R} копій`);
  let best: Rec | undefined;
  for (const r of reachable) {
    const rec = r.local(key);
    if (rec && (best === undefined || rec.version > best.version)) best = rec;
  }
  return best;
}

// ЗРЕШТОЮ: одна найближча копія, без кворуму. Доступно навіть у розкол,
// але віддає те, що ця копія знає зараз, — хай і застаріле.
function readEventual(key: string, local: Replica): Rec | undefined {
  return local.local(key);
}

// Ворота доступу читають право СТРОГО; будь-який сумнів (нема кворуму) → «ні».
function mayOpen(key: string, reachable: Replica[]): boolean {
  try {
    return readStrong(key, reachable)?.value === true;   // нема запису / active=false → ні
  } catch (e) {
    if (e instanceof NoQuorum) return false;             // fail-closed: за сумніву — замкнено
    throw e;
  }
}

// Телеметрію читаємо ЗРЕШТОЮ — застаріле число нікому не шкодить.
function latestTemp(key: string, local: Replica): number | undefined {
  return readEventual(key, local)?.value as number | undefined;
}
