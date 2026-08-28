const CODES: Set<string> = new Set(loadJSON("surface/error-codes.json").codes);  // відкритий реєстр

const LEAK = [                                     // чого НЕ сміє бути в message
  /\bat\s+.+:\d+/,                                 // кадр стека: at fn (file.ts:12)
  /\bselect\b[\s\S]+\bfrom\b/i,                    // SQL
  /(?:[A-Za-z]:\\|\/(?:home|var|usr|etc)\/)/,      // шлях у файловій системі
  /\b(exception|traceback|stack)\b/i,             // назви внутрішнього механізму
];

function lintError(body: unknown): string[] {
  const errs: string[] = [];
  const top = body && typeof body === "object" ? Object.keys(body) : [];
  if (top.length !== 1 || top[0] !== "error")     // 1. рівно { error: … }, нічого зайвого
    return [`конверт не { error: … }: {${top.join(",")}}`];
  const e = (body as { error: Record<string, unknown> }).error ?? {};
  if (Object.keys(e).sort().join(",") !== "code,message")   // жодних stack/sql/detail поруч
    errs.push(`error має бути {code,message}, а не {${Object.keys(e).join(",")}}`);
  if (!CODES.has(e.code as string))               // 2. код — із відкритого набору
    errs.push(`код "${e.code}" не зареєстрований`);
  if (LEAK.some(re => re.test(String(e.message)))) // 3. без нутрощів
    errs.push(`message виказує нутрощі: "${e.message}"`);
  return errs;
}
