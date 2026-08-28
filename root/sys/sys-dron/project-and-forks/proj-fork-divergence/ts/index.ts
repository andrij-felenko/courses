#!/usr/bin/env -S npx tsx
// Борг злиття форку: площа дотику зі спільним кодом і зона зіткнення.
import { execFileSync } from "node:child_process";
import { parseArgs } from "node:util";

// maxBuffer за замовчуванням — 1 МБ; diff форку station легко його перевищує.
const git = (...args: string[]): string =>
  execFileSync("git", args, { encoding: "utf8", maxBuffer: 256 << 20 });

function changed(base: string, tip: string, exclude: string[]): Map<string, string> {
  const out = new Map<string, string>();
  const args = ["diff", "--name-status", "-M", base, tip, "--",
                ...exclude.map((p) => `:(exclude)${p}`)];
  for (const ln of git(...args).split("\n")) {
    const cols = ln.split("\t");
    if (cols.length < 2) continue;
    // "M\tsrc/Vehicle.cc" або "R096\tстара\tнова" — беремо НОВИЙ шлях
    out.set(cols.at(-1)!, cols[0][0]);
  }
  return out;
}

function upstreamChurn(base: string, upstream: string, paths: string[]): Map<string, number> {
  const out = new Map<string, number>();
  for (let i = 0; i < paths.length; i += 200) {          // довжина командного рядка обмежена
    const part = paths.slice(i, i + 200);
    const raw = git("diff", "--numstat", "--no-renames", base, upstream, "--", ...part);
    for (const ln of raw.split("\n")) {
      const [add, del, path] = ln.split("\t");
      if (!path) continue;
      out.set(path, add === "-" ? 0 : Number(add) + Number(del));   // "-" = бінарний
    }
  }
  return out;
}

// тека файла, обрізана до depth сегментів: src/Vehicle/V.cc → src/Vehicle
const group = (p: string, depth = 2): string => {
  const dirs = p.split("/").slice(0, -1);          // ім'я файла — не тека
  return dirs.length ? dirs.slice(0, depth).join("/") : "(корінь)";
};

// українське узгодження: 1 файл, 2 файли, 5 файлів, 12 файлів
const plural = (n: number, one: string, few: string, many: string): string => {
  if ([11, 12, 13, 14].includes(n % 100)) return many;
  if (n % 10 === 1) return one;
  return [2, 3, 4].includes(n % 10) ? few : many;
};

const { values } = parseArgs({
  options: {
    upstream: { type: "string", default: "upstream/master" },
    head:     { type: "string", default: "HEAD" },
    overlay:  { type: "string", default: "custom/" },
    exclude:  { type: "string", multiple: true, default: [] },
    budget:   { type: "string", default: "0" },
  },
});

const base = git("merge-base", values.upstream!, values.head!).trim();
const [behind, ahead] = git("rev-list", "--left-right", "--count",
                            `${values.upstream}...${values.head}`).trim().split(/\s+/);

const mine = changed(base, values.head!, values.exclude!);
const theirs = changed(base, values.upstream!, values.exclude!);

const paths = [...mine.keys()];
const overlay = paths.filter((p) => p.startsWith(values.overlay!));
const rest = paths.filter((p) => !p.startsWith(values.overlay!));
const added = rest.filter((p) => mine.get(p) === "A");
const touched = rest.filter((p) => mine.get(p) !== "A");     // площа дотику
const collide = touched.filter((p) => theirs.has(p)).sort();

const churn = upstreamChurn(base, values.upstream!, collide);
const files = new Map<string, number>();
const lines = new Map<string, number>();
for (const p of collide) {
  const d = group(p);
  files.set(d, (files.get(d) ?? 0) + 1);
  lines.set(d, (lines.get(d) ?? 0) + (churn.get(p) ?? 0));
}

const share = touched.length ? (100 * collide.length) / touched.length : 0;
console.log(`точка розгалуження        : ${base.slice(0, 10)}`);
console.log(`комітів позаду / попереду : ${behind} / ${ahead}\n`);
console.log("ваші зміни від точки розгалуження");
console.log(`  у теці накладки ${values.overlay}          ${overlay.length}`);
console.log(`  нові файли у спільних теках  ${added.length}`);
console.log(`  ПРАВКИ спільних файлів       ${touched.length}   ← площа дотику\n`);
console.log(`апстрим від тієї ж точки зачепив ${theirs.size} `
          + `${plural(theirs.size, "файл", "файли", "файлів")}`);
console.log(`зона зіткнення: ${collide.length} із ${touched.length} `
          + `(${share.toFixed(0)}%) — тут буде ручна робота\n`);

for (const [d, n] of [...files].sort((x, y) => y[1] - x[1]).slice(0, 12)) {
  const ln = lines.get(d) ?? 0;
  console.log(`  ${d.padEnd(32)} ${String(n).padStart(4)} `
            + `${plural(n, "файл", "файли", "файлів").padEnd(7)} `
            + `${String(ln).padStart(7)} ${plural(ln, "рядок", "рядки", "рядків")} апстриму`);
}

process.exit(Number(values.budget) && collide.length > Number(values.budget) ? 1 : 0);
