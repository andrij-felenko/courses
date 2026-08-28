// ── Запобіжник 1: перетягнуте обмеження ──────────────────────────────
type Landed =
  | { readonly ok: true; readonly journal: readonly Event[] }
  | { readonly ok: false; readonly wiped: readonly string[]; readonly why: string };

const land = (journal: readonly Event[], fact: Fact): Landed => {
  const { alive } = replay(journal, fact.when);   // стан СТАНОМ НА дату факта
  if (alive.length > 0 && !alive.some((o) => fact.holds(o))) {
    const wiped = alive.map((o) => o.name);
    return {
      ok: false, wiped,
      why: `факт «${fact.says}» не лишає живим НІКОГО (стирає: ${wiped.join(", ")}). ` +
        `Це не збіжність, а порожній перетин: або обмеження перетягнуте, або в наборі ` +
        `бракує кандидата. Розширюй набір чи послаблюй межу — але свідомо й у журналі.`,
    };
  }
  return { ok: true, journal: [...journal, { kind: "learned", fact }] };
};

// ── Запобіжник 2: вибуття, що тримається лише на здогаді ─────────────
const provisional = (st: State): string[] =>
  [...st.killedBy]
    .filter(([, killers]) => !killers.some((f) => PROVEN.includes(f.evidence)))
    .map(([name]) => name)
    .sort();

// ── Присуд: єдине, заради чого все це будувалося ─────────────────────
type Verdict = "ПОРОЖНЬО" | "ЗВУЖУЄМО" | "ЗАСТРЯГЛО" | "УДАВАНА ЗБІЖНІСТЬ" | "ЗБІГЛОСЯ";

const verdict = (st: State, today: Day, deadline: Day): readonly [Verdict, string] => {
  if (st.alive.length === 0) return ["ПОРОЖНЬО", "живих не лишилось — перетин порожній"];
  const unproven = provisional(st);
  if (st.alive.length === 1) {
    const one = st.alive[0].name;
    return unproven.length > 0
      ? ["УДАВАНА ЗБІЖНІСТЬ", `живий один (${one}), але вибуття ${unproven.join(", ")} ` +
         `тримається лише на здогаді — доведи факт або поверни варіант у набір`]
      : ["ЗБІГЛОСЯ", `живий один (${one}), кожне вибуття доведене — фіксуй`];
  }
  const names = st.alive.map((o) => o.name).join(", ");
  const left = daysBetween(today, deadline);
  return left <= 0
    ? ["ЗАСТРЯГЛО", `живих ще ${st.alive.length} (${names}), а дедлайн збіжності минув ` +
       `${-left} дн. тому: задарма фактів більше не буде — обирай зараз`]
    : ["ЗВУЖУЄМО", `живих ${st.alive.length} (${names}); до дедлайну ${left} дн. — ` +
       `який факт уб'є котрого?`];
};

// ── Відповідь на питання «чому не взяли…» ────────────────────────────
const explain = (st: State, name: string): string => {
  const killers = st.killedBy.get(name);
  if (!killers) return `${name} — живий`;
  return killers
    .map((f) => `${name} ✗ ${f.says}   [${f.id} · ${f.evidence} · ${f.source} · ${f.when}]`)
    .join("\n");
};
