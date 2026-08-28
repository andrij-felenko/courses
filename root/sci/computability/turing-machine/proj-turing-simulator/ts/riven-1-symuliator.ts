const BL = "␣";

type Dir = "L" | "R";
type Rule = { write: string; move: Dir; next: string };
type Delta = Map<string, Rule>;
type Verdict = "ПРИЙНЯТО" | "ВІДКИНУТО" | "НЕ ЗНАЮ";

const key = (q: string, c: string) => `${q},${c}`;
const table = (rows: [string, string, string, Dir, string][]): Delta =>
  new Map(rows.map(([q, c, write, move, next]) => [key(q, c), { write, move, next }]));

function run(delta: Delta, w: string, start = "q0", limit = 10_000, trace = false) {
  const tape = new Map<number, string>([...w].map((c, i) => [i, c])); // словник, не масив
  let q = start, head = 0;
  for (let steps = 0; steps <= limit; steps++) {
    if (trace) console.log(snapshot(tape, head, q));
    if (q === "qa") return { v: "ПРИЙНЯТО" as Verdict, steps, tape: content(tape) };
    if (q === "qr") return { v: "ВІДКИНУТО" as Verdict, steps, tape: content(tape) };
    const rule = delta.get(key(q, tape.get(head) ?? BL));   // уся δ — один пошук
    if (!rule) return { v: "ВІДКИНУТО" as Verdict, steps, tape: content(tape) };
    tape.set(head, rule.write);
    head += rule.move === "R" ? 1 : -1;
    q = rule.next;
  }
  return { v: "НЕ ЗНАЮ" as Verdict, steps: limit, tape: content(tape) };
}

function snapshot(tape: Map<number, string>, head: number, q: string) {
  const ks = [...tape.keys(), head];
  let cells = "";
  for (let i = Math.min(...ks); i <= Math.max(...ks); i++)
    cells += (i === head ? "▸" : " ") + (tape.get(i) ?? BL);
  return (q + ":").padEnd(3) + cells;
}

const content = (tape: Map<number, string>) =>
  [...tape.keys()].sort((a, b) => a - b).map((i) => tape.get(i)!).join("").replace(/^␣+|␣+$/g, "");

// таблиця δ машини, що перевіряє мову {0ⁿ1ⁿ}: викреслюємо пари 0↔1 позначками X та Y
const D01 = table([
  ["q0", "0", "X", "R", "q1"], ["q0", "Y", "Y", "R", "q3"], ["q0", BL, BL, "R", "qa"],
  ["q1", "0", "0", "R", "q1"], ["q1", "Y", "Y", "R", "q1"], ["q1", "1", "Y", "L", "q2"],
  ["q2", "0", "0", "L", "q2"], ["q2", "Y", "Y", "L", "q2"], ["q2", "X", "X", "R", "q0"],
  ["q3", "Y", "Y", "R", "q3"], ["q3", BL, BL, "R", "qa"],
]);
