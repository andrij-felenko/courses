const REGISTER: Risk[] = [
  { id: "R1", desc: "Vendor-API відмовить під піком", p: 0.30, L: 500_000,
    trigger: "p95 latency > 800 мс",   owner: "Оля",   state: "mitigating" },
  { id: "R2", desc: "Витік через невчасний патч",     p: 0.10, L: 800_000,
    trigger: "CVE у прямій залежності", owner: "Тарас", state: "watched" },
  { id: "R3", desc: "Ключова людина звільниться",     p: 0.20, L: 300_000,
    trigger: "вигорання видно на 1:1",  owner: "Ліда",  state: "open" },
  { id: "R4", desc: "Схема бази застигне",            p: 0.25, L: 120_000,
    trigger: "міграція триває > 2 год", owner: "Оля",   state: "open" },
  { id: "R0", desc: "Стара інтеграція впаде",         p: 0.40, L: 200_000,
    trigger: "—",                       owner: "Тарас", state: "closed" }, // закритий!
];

function rank(reg: readonly Risk[]): void {
  const live = reg.filter((r) => !DEAD.has(r.state));
  for (const r of [...live].sort((a, b) => exposure(b) - exposure(a))) {
    console.log(
      `  ${r.id}  ${r.desc.padEnd(30).slice(0, 30)}  p=${r.p.toFixed(2)}` +
      `  →  ${exposure(r).toFixed(0).padStart(8)}  [${r.owner}]`,
    );
  }
  console.log(`  Σ портфеля (активні рядки) = ${portfolio(reg).toFixed(0)}`);
}

rank(REGISTER);
