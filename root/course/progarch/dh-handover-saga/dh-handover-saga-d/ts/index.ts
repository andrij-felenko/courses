type Kind = "compensatable" | "pivot" | "retriable";

interface Step {
  name: string;
  kind: Kind;
  run: (h: Handover) => Promise<void>;          // локальна транзакція у своєму контексті
  compensate?: (h: Handover) => Promise<void>;  // зустрічна дія — лише до півота
}

// Порядок і є суть: усе зворотне ДО півота, усе обов'язкове — ПІСЛЯ.
const HANDOVER: Step[] = [
  { name: "freeze",          kind: "compensatable", run: freeze,          compensate: unfreeze },
  { name: "revokeAccess",    kind: "compensatable", run: revokeOldKeys,   compensate: restoreOldKeys },
  { name: "awaitClaim",      kind: "compensatable", run: waitForNewOwner, compensate: cancelClaim },
  { name: "transferAndWipe", kind: "pivot",         run: transferAndShred },   // ← точка неповороту
  { name: "rebindDevices",   kind: "retriable",     run: reissueCerts },
  { name: "openBilling",     kind: "retriable",     run: switchBilling },
  { name: "welcome",         kind: "retriable",     run: notifyNewOwner },
];

async function drive(h: Handover) {
  const done: Step[] = [];
  for (const step of HANDOVER) {
    try {
      await step.run(h);              // кожен run ідемпотентний: повтор ≠ подвоєння
      done.push(step);
    } catch (err) {
      if (step.kind === "retriable") throw err;   // після півота — не скасовуй, повторюй
      for (const s of [...done].reverse())        // до півота — задкуй, відкочуючи
        await s.compensate?.(h);
      return aborted(h);
    }
  }
}
