// risk-register.ts — реєстр Digital Homes як дані, що самі себе лінтять.
// Запуск у CI:  npx tsx risk-register.ts   (ненульовий код виходу = білд червоний)

type Probability = "low" | "med" | "high" | "unknown";
type Impact      = "minor" | "major" | "catastrophic";
type State       = "open" | "watching" | "accepted" | "closed";

interface Risk {
  id: string;
  what: string;              // подія, не абстракція
  probability: Probability;
  impact: Impact;
  trigger: string;           // ознака-тригер; "" = ще нема
  owner: string;             // жива людина; "" = ще нема
  reviewed: string;          // "YYYY-MM-DD" — коли рядок востаннє чіпали
  state: State;
}

// Щаблі, не проценти: три поділки на осі — стільки, скільки чесно можна оцінити.
const P_SCORE: Record<Probability, number> = { low: 1, med: 2, high: 3, unknown: 3 };
//                                                                       ^ невідома коштує
//   як найгірша: поки зрізом не збили туман, «відоме невідоме» тримаємо у верхньому куті.
const I_SCORE: Record<Impact, number> = { minor: 1, major: 3, catastrophic: 4 };

const exposure = (r: Risk): number => P_SCORE[r.probability] * I_SCORE[r.impact];

// рідкісне ≠ нестрашне: у катастрофи хвіст без дна — важка й на низькій імовірності.
const isHeavy  = (r: Risk): boolean => exposure(r) >= 6 || r.impact === "catastrophic";
const isActive = (r: Risk): boolean => r.state === "open" || r.state === "watching";
