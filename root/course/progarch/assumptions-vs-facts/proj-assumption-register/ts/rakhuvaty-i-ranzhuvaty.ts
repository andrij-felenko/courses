function load(path: string): Assumption[] {
  const raw = parse(readFileSync(path, "utf8")) as any[];
  return raw.map((r) => {
    const a: Assumption = {
      id: r.id, claim: r.claim, kind: r.kind,
      pWrong: r.p_wrong, loss: r.loss, costToCheck: r.cost_to_check,
      method: r.method, signpost: r.signpost,
      state: r.state, decision: r.decision, irreversible: r.irreversible,
    };
    if (!(a.pWrong >= 0 && a.pWrong <= 1))
      throw new Error(`${a.id}: P поза [0,1] — ${a.pWrong}`);
    if (a.loss < 0 || a.costToCheck < 0)
      throw new Error(`${a.id}: відʼємна ціна`);
    return a;
  });
}

const ranked = (reg: Assumption[]): Assumption[] =>
  reg.filter((a) => LIVE.includes(a.state))
     .sort((x, y) => expectedLoss(y) - expectedLoss(x));

const checkFirst = (reg: Assumption[]): Assumption[] =>
  ranked(reg).filter(worthChecking);

function report(reg: Assumption[]): void {
  console.log("що перевіряти першим (спадання очікуваної втрати):");
  checkFirst(reg).forEach((a, i) => {
    const flag = a.irreversible ? "  ⟵ ГЕЙТ незворотного кроку" : "";
    const n = String(i + 1).padStart(2);
    console.log(`${n}. ${expectedLoss(a).toFixed(1).padStart(5)}  ${a.claim}${flag}`);
  });
  const watch = reg.filter((a) => a.state === "accepted");
  if (watch.length) {
    console.log("\nпід сигнальним знаком (стежити, не перевіряти):");
    for (const a of watch) console.log(`  • ${a.claim} → знак: ${a.signpost}`);
  }
}
