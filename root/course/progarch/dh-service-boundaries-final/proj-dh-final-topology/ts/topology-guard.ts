// arch/topology-guard.ts — сторож фінальної топології DH. Валить збірку на ТРЬОХ зрадах.
// Джерело правди — DEPLOYMENTS і SEAMS; тут лише вирок над знайденим у коді.
import { DEPLOYMENTS, SEAMS, Style } from "./topology";
type Edge = { from: string; to: string; kind: Style };

const declared = new Map<string, Style>(SEAMS.map(s => [`${s.from}→${s.to}`, s.style]));
const KNOWN_DBS = new Set(Object.values(DEPLOYMENTS).map(d => d.db).filter(Boolean));

// Сканер уже пройшов код кожного сервіса й дав чотири списки знайденого:
type Scan = {
  calls:  [string, string][];   // [сервіс, ціль]  ← rpc.call("<ціль>")       — СИНХРОННИЙ шов
  pubs:   [string, string][];   // [сервіс, топік] ← bus.publish("<топік>")   — асинхронний
  subs:   [string, string][];   // [сервіс, топік] ← bus.subscribe("<топік>")
  dbRefs: [string, string][];   // [сервіс, база]  ← DSN / "<база>."          — доступ до бази
};

// СИНХРОННЕ ребро видно на місці виклику. АСИНХРОННЕ — ні: продюсер називає ТОПІК,
// а не ціль. Тож async-ребра відновлюємо як «продюсери × споживачі того самого топіка».
function observed(scan: Scan): Edge[] {
  const edges: Edge[] = scan.calls.map(([from, to]) => ({ from, to, kind: "sync" }));
  const pubsByTopic = new Map<string, string[]>();
  for (const [dep, topic] of scan.pubs) {
    if (!pubsByTopic.has(topic)) pubsByTopic.set(topic, []);
    pubsByTopic.get(topic)!.push(dep);
  }
  for (const [sub, topic] of scan.subs)
    for (const pub of pubsByTopic.get(topic) ?? [])
      if (pub !== sub) edges.push({ from: pub, to: sub, kind: "async" });   // ребро pub → sub
  return edges;
}

export function violations(scan: Scan): string[] {
  const bad: string[] = [];
  const edges = observed(scan);
  for (const e of edges)                                          // 1) РЕБРО ПОЗА МАПОЮ
    if (!declared.has(`${e.from}→${e.to}`))
      bad.push(`ребро поза мапою: ${e.from} → ${e.to} (${e.kind})`);
  for (const [dep, db] of scan.dbRefs)                           // 2) ЧУЖА БАЗА
    if (KNOWN_DBS.has(db) && DEPLOYMENTS[dep]?.db !== db)
      bad.push(`чужа база: ${dep} читає ${db} (володіє нею інший сервіс)`);
  for (const e of edges)                                          // 3) СТИЛЬ ЗРАДЖЕНО
    if (e.kind === "sync" && declared.get(`${e.from}→${e.to}`) === "async")
      bad.push(`шов ${e.from} → ${e.to} оголошено асинхронним, а зустрів синхронний rpc.call`);
  return bad;
}

export function main(scan: Scan): number {
  const bad = violations(scan);
  if (bad.length === 0) { console.log("топологія DH тримається"); return 0; }
  console.error("ЗРАДА ТОПОЛОГІЇ DH:");
  for (const b of bad) console.error("  " + b);
  return 1;                       // exit 1 → CI кожного сервіса червоний → merge заблоковано
}
