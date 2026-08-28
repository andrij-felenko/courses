const blocksCommit = (reg: Assumption[]): Assumption[] =>
  ranked(reg).filter((a) => a.irreversible && worthChecking(a));

function gate(reg: Assumption[]): void {
  const blockers = blocksCommit(reg);
  if (blockers.length) {
    const lines = blockers.map((a) =>
      `  ✗ ${a.id}: ${a.claim} ` +
      `(очік. втрата ${expectedLoss(a).toFixed(0)}, перевірка ${a.costToCheck})`
    ).join("\n");
    console.error("НЕЗВОРОТНИЙ КРОК ЗАБЛОКОВАНО — спершу зніми перевіркою:\n" + lines);
    process.exit(1);
  }
  console.log("гейт відкрито: усі несучі припущення незворотного кроку зняті");
}

// у CI перед заливкою прошивки в поле:
gate(load("assumptions.yml"));
