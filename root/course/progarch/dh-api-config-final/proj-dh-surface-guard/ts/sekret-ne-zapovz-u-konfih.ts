// Ключі, де значення-секрет НЕ має права лежати відкритим текстом.
const SECRET_KEY = /(pass(word)?|pwd|secret|token|api[-_]?key|private[-_]?key|cred|auth)/i;

// Ентропія Шеннона: скільки біт несе символ. Випадкові токени — високі; слова — низькі.
function shannon(s: string): number {
  const freq = new Map<string, number>();
  for (const ch of s) freq.set(ch, (freq.get(ch) ?? 0) + 1);
  let h = 0;
  for (const n of freq.values()) { const p = n / s.length; h -= p * Math.log2(p); }
  return h;                                       // біт на символ
}

const isRef = (v: unknown): boolean =>            // посилання на секрет — законна форма
  typeof v === "object" && v !== null && typeof (v as { secret?: unknown }).secret === "string";

const ALLOW = [                                   // відома БЕЗПЕЧНА висока ентропія
  /^[0-9a-f]{7,40}$/i,                            // git SHA
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i,  // UUID
  /-----BEGIN (PUBLIC KEY|CERTIFICATE)-----/,     // публічний ключ — не таємниця
];

function scanConfig(cfg: Record<string, unknown>): Violation[] {
  const out: Violation[] = [];
  for (const [key, val] of Object.entries(cfg)) {
    if (isRef(val)) continue;                      // {secret:"…"} — правильний спосіб тримати секрет
    if (typeof val !== "string") continue;
    if (ALLOW.some(re => re.test(val))) continue;  // навмисний виняток
    const looksSecret =
      SECRET_KEY.test(key) ||                      // СИЛЬНИЙ сигнал: імʼя ключа
      (val.length >= 20 && shannon(val) >= 4.0);   // слабший: висока ентропія
    if (looksSecret)
      out.push({ path: `config.${key}`,
                 reason: "схоже на секрет-значення — тримай як посилання {secret:\"…\"}" });
  }
  return out;
}
