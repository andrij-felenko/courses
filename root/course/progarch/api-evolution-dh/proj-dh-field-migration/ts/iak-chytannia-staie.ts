function parseFields(q: unknown): Set<string> | null {
  if (typeof q !== "string" || q.trim() === "") return null;   // нема ?fields → уся форма
  return new Set(q.split(",").map(s => s.trim()).filter(Boolean));
}

function project<T extends object>(body: T, fields: Set<string>): Partial<T> {
  const out: Partial<T> = {};
  for (const k of Object.keys(body) as (keyof T)[]) {
    if (fields.has(k as string)) out[k] = body[k];
  }
  return out;
}
