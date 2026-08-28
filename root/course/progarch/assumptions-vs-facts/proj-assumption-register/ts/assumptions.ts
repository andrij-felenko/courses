// assumptions.ts — журнал припущень, що рахує й спиняє
import { readFileSync } from "node:fs";
import { parse } from "yaml";                 // npm i yaml

type State = "open" | "checking" | "accepted" | "fact" | "broken";
const LIVE: State[] = ["open", "checking", "accepted"]; // ще важать на рішення

interface Assumption {
  id: string;
  claim: string;
  kind: "несуче" | "побутове" | "продуктове";
  pWrong: number;          // 0..1
  loss: number;            // людино-дні, якщо хибне
  costToCheck: number;     // людино-дні на перевірку
  method: string;          // ЧИМ перевіряємо, не «перевірити»
  signpost: string;        // поріг, за яким припущення вважаємо зламаним
  state: State;
  decision: string;        // яке рішення (ADR) на ньому стоїть
  irreversible: boolean;   // чи веде те рішення до незворотного кроку
}

const expectedLoss = (a: Assumption): number =>
  LIVE.includes(a.state) ? a.pWrong * a.loss : 0;

const worthChecking = (a: Assumption): boolean =>
  // перевіряти має сенс, лише поки не прийняли й не довели
  (a.state === "open" || a.state === "checking") &&
  a.costToCheck < expectedLoss(a);
