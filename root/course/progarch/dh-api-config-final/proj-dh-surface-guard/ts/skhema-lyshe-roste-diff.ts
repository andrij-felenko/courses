// Підпис поля: скаляр або перелік (відкритий/закритий).
type Sig =
  | { kind: "scalar"; type: "string" | "number" | "boolean" }
  | { kind: "enum"; open: boolean; values: string[] };

type Field   = { sig: Sig; required: boolean };
type Surface = Record<string, Field>;          // "DeviceDTO.temperature.unit" → Field
type Violation = { path: string; reason: string };

// Чи СУМІСНА поточна форма поля з базовою? null = сумісно; рядок = причина зламу.
function breakOf(base: Field, cur: Field): string | null {
  if (base.required && !cur.required)
    return "поле більше не гарантоване (було обовʼязкове)";
  const b = base.sig, c = cur.sig;
  if (b.kind !== c.kind)               return `тип змінив природу: ${b.kind} → ${c.kind}`;
  if (b.kind === "scalar" && c.kind === "scalar" && b.type !== c.type)
    return `тип поля: ${b.type} → ${c.type}`;
  if (b.kind === "enum" && c.kind === "enum") {
    const removed = b.values.filter(v => !c.values.includes(v));
    if (removed.length)     return `зникло значення переліку: ${removed.join(", ")}`;
    const added = c.values.filter(v => !b.values.includes(v));
    if (added.length && !b.open)
      return `новий стан у ЗАКРИТОМУ переліку: ${added.join(", ")}`;   // ← ламає exhaustive-клієнта
    if (b.open && !c.open)  return "відкритий перелік став закритим";
  }
  return null;   // додане поле, ширший відкритий перелік, нова опція — усе сумісно
}

// Поверхня мусить лише РОСТИ проти базового знімка.
function diffSurface(base: Surface, cur: Surface, deprecated: Set<string>): Violation[] {
  const out: Violation[] = [];
  for (const path of Object.keys(base)) {
    if (!(path in cur)) {
      if (!deprecated.has(path))
        out.push({ path, reason: "поле зникло без запису про деприкейшн" });
      continue;                        // зникло, АЛЕ є запис → кероване вилучення
    }
    const why = breakOf(base[path], cur[path]);
    if (why) out.push({ path, reason: why });
  }
  // Нові поля в cur, яких нема в base, — додавання: свідомо НЕ порушення.
  return out;
}
