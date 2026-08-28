type Belief =
  | { kind: "fact"; claim: string; evidence: string }
  | { kind: "assumption"; claim: string;
      pWrong: number; lossIfWrong: number; costToCheck: number };

function shouldValidateNow(b: Belief): boolean {
  if (b.kind === "fact") return false;         // доказ уже на руках — перевіряти нічого
  const expectedLoss = b.pWrong * b.lossIfWrong;
  return b.costToCheck < expectedLoss;         // купуй інформацію, поки вона дешевша за втрату
}

const lockApi: Belief = {
  kind: "assumption", claim: "модуль замка тримає API ≥ 2 роки",
  pWrong: 0.3, lossIfWrong: 120, costToCheck: 3,
};
shouldValidateNow(lockApi); // true → перевірити до коміту
