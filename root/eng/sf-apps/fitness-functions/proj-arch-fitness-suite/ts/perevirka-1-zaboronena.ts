function reaches(g: Graph, src: string, dst: string): boolean {
  // Чи є напрямлений шлях src → … → dst.
  const seen = new Set([src]);
  const stack = [src];
  while (stack.length) {
    const u = stack.pop()!;
    for (const v of g.get(u) ?? []) {   // порядок обходу не важить — шукаємо сам факт шляху
      if (v === dst) return true;
      if (!seen.has(v)) { seen.add(v); stack.push(v); }
    }
  }
  return false;
}

function checkForbidden(g: Graph, rules: [string, string][]): string[] {
  // rules: пари (X, Y) зі змістом «X не сміє досягати Y».
  return rules
    .filter(([x, y]) => reaches(g, x, y))
    .map(([x, y]) => `${x} ⇏ ${y}: є шлях ${x} → … → ${y}`);
}
