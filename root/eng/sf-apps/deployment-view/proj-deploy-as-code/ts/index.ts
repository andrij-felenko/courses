import { readFileSync } from "node:fs";
import { parse } from "yaml";              // npm i yaml

const ZONE = "node.labels.zone";           // мітка вузла: в якій зоні він стоїть

interface Deploy {
  replicas?: number;
  placement?: { constraints?: string[]; preferences?: { spread?: string }[] };
}
interface Stack { services?: Record<string, { deploy?: Deploy }>; }
type Verdict = "single" | "ok" | "warn" | "fail";
interface Report { name: string; copies: number; verdict: Verdict; note: string; }

// ── 1. База + оверлей → глибоке злиття (як `docker compose config`) ──────────
const isObj = (v: unknown): v is Record<string, unknown> =>
  typeof v === "object" && v !== null && !Array.isArray(v);

function deepMerge(base: any, over: any): any {
  if (!isObj(base) || !isObj(over)) return over;
  const out: Record<string, unknown> = { ...base };
  for (const [k, v] of Object.entries(over))
    out[k] = k in out ? deepMerge(out[k], v) : v;
  return out;
}
const loadStack = (...paths: string[]): Stack =>
  paths.map((p) => parse(readFileSync(p, "utf8")) ?? {}).reduce(deepMerge, {}) as Stack;

// ── 2. У яких зонах placement ГАРАНТУЄ копії ─────────────────────────────────
function zoneCover(deploy: Deploy = {}): { pinned: Set<string>; spreads: boolean } {
  const place = deploy.placement ?? {};
  const pinned = new Set<string>();
  for (const c of place.constraints ?? []) {
    const m = c.match(/node\.labels\.zone\s*==\s*(\S+)/);
    if (m) pinned.add(m[1]);
  }
  const spreads = (place.preferences ?? []).some((p) => p.spread === ZONE);
  return { pinned, spreads };
}

// ── 3. Вердикт на один логічний контейнер ────────────────────────────────────
function judge(name: string, spec: { deploy?: Deploy }): Report {
  const deploy = spec.deploy ?? {};
  const copies = deploy.replicas ?? 1;
  const { pinned, spreads } = zoneCover(deploy);
  if (copies <= 1)
    return { name, copies, verdict: "single", note: "одна копія — надлишковості нема" };
  if (pinned.size >= 2 || spreads)
    return { name, copies, verdict: "ok", note: "копії рознесено по зонах" };
  if (pinned.size === 1)
    return { name, copies, verdict: "fail",
             note: `усі прибито до зони ${[...pinned][0]} — надлишковість уявна` };
  return { name, copies, verdict: "warn",
           note: "нема правила зон — планувальник може скласти копії в одну зону" };
}
const analyze = (s: Stack): Report[] =>
  Object.entries(s.services ?? {})
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([n, spec]) => judge(n, spec));

// ── 4. Паритет: набір логічних сервісів мусить збігатися між середовищами ─────
function parityGap(dev: Stack, prod: Stack): string[] {
  const d = new Set(Object.keys(dev.services ?? {}));
  const p = new Set(Object.keys(prod.services ?? {}));
  return [...new Set([...d, ...p])].filter((s) => d.has(s) !== p.has(s)).sort();
}

// ── 5. Гейт CI: fail або зламаний паритет валить збірку (код виходу 1) ────────
const dev = loadStack("compose.yaml", "compose.dev.yaml");
const prod = loadStack("compose.yaml", "compose.prod.yaml");
const mark: Record<Verdict, string> = { ok: "OK  ", single: "·   ", warn: "WARN", fail: "FAIL" };
let bad = false;
console.log("== prod ==");
for (const r of analyze(prod)) {
  console.log(`${mark[r.verdict]} ${r.name.padEnd(7)} копій: ${r.copies}  ${r.note}`);
  bad ||= r.verdict === "fail";
}
const gap = parityGap(dev, prod);
if (gap.length) { console.log("PARITY  лише в одному середовищі:", gap.join(", ")); bad = true; }
process.exit(bad ? 1 : 0);
