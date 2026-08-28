interface Diff {
  path: string;
  status: "match" | "mismatch" | "error";
  details?: string;
}
declare function recordDiff(d: Diff): void;   // → метрика/лог розбіжностей

// Порівняння відповідей. НЕ «==»: у відповідях повно полів, що законно
// різняться (timestamp генерації, порядок ключів, службові заголовки).
// Звіряємо лише СУТЬ, нормалізувавши обидві. Тут — тіло як канонічний JSON.
function bodiesEqual(a: unknown, b: unknown): boolean {
  return canonical(a) === canonical(b);
}
function canonical(v: unknown): string {
  if (v === null || typeof v !== "object") return JSON.stringify(v);
  if (Array.isArray(v)) return "[" + v.map(canonical).join(",") + "]";
  // ключі за абеткою — інакше {a,b} і {b,a} здались би різними
  const keys = Object.keys(v as object).sort();
  return "{" + keys.map(k => JSON.stringify(k) + ":" +
              canonical((v as any)[k])).join(",") + "}";
}

// Читання з тінню. Клієнт ЗАВЖДИ отримує результат контролю (старе).
async function readWithShadow(rule: RouteRule, req: Request): Promise<Response> {
  const path = new URL(req.url).pathname;
  const control = await callLegacy(req);           // старе — його й віддамо

  if (rule.shadow) {
    // кандидат виконуємо, але його падіння НЕ сміє зачепити клієнта
    try {
      const candidate = await callService(rule.serviceUrl, req);
      const a = await control.clone().json();
      const b = await candidate.clone().json();
      recordDiff({ path,
        status: bodiesEqual(a, b) ? "match" : "mismatch",
        details: bodiesEqual(a, b) ? undefined
               : `control=${JSON.stringify(a)} candidate=${JSON.stringify(b)}` });
    } catch (e) {
      // кандидат упав або відповів не-JSON — це теж цінний сигнал
      recordDiff({ path, status: "error", details: String(e) });
    }
  }
  return control;                                  // клієнтові — тільки старе
}
