const byThreat = (reg: Risk[]): Risk[] =>
  // спад експозиції, за рівної — важчий вплив вище; .sort стабільний, тож порядок ties сталий
  [...reg].sort((a, b) => exposure(b) - exposure(a) || I_SCORE[b.impact] - I_SCORE[a.impact]);

interface Violation { id: string; detail: string; }

function daysIdle(reviewedISO: string, today: Date): number {
  const then = Date.parse(reviewedISO + "T00:00:00Z");
  const now  = Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate());
  return Math.floor((now - then) / 86_400_000);
}

function lint(reg: Risk[], today: Date, staleDays = 14): Violation[] {
  const out: Violation[] = [];
  for (const r of reg) {
    if (!isActive(r)) continue;                 // прийняте/закрите свідомо не чіпаємо
    const idle = daysIdle(r.reviewed, today);
    if (idle > staleDays)
      out.push({ id: r.id, detail: `застій: ${idle} дн. без перегляду (поріг ${staleDays})` });
    if (isHeavy(r)) {                           // важкий і відкритий → мусить мати тригер і власника
      if (!r.trigger.trim()) out.push({ id: r.id, detail: "важкий відкритий ризик без тригера" });
      if (!r.owner.trim())   out.push({ id: r.id, detail: "важкий відкритий ризик без власника" });
    }
  }
  return out;
}

const LABEL: Record<State, string> = {
  open: "відкритий", watching: "під наглядом", accepted: "прийнято", closed: "закритий",
};

function report(reg: Risk[], today: Date): number {
  console.log(`Реєстр Digital Homes — ${reg.length} рядків, станом на ${today.toISOString().slice(0, 10)}\n`);
  console.log("  експ  стан          рядок");
  for (const r of byThreat(reg))
    console.log(`  ${String(exposure(r)).padStart(4)}  ${LABEL[r.state].padEnd(12)}  ${r.what}`);

  const problems = lint(reg, today);
  console.log("\nЛІНТЕР");
  if (problems.length === 0) {
    console.log("  чисто — жодного застояного чи напівпорожнього важкого рядка");
    return 0;
  }
  for (const p of problems) console.log(`  ✗  ${p.id.padEnd(18)} ${p.detail}`);
  console.log(`\n${problems.length} порушення → реєстр застоявся, CI падає`);
  return 1;
}

// У CI today = new Date(); тут фіксуємо дату для відтворюваного прикладу.
process.exit(report(REGISTER, new Date("2026-03-24T00:00:00Z")));
