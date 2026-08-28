// Стан рядка як об'єднання рядкових літералів — вичерпний і перевірний.
type State =
  | "open" | "watched" | "mitigating" // активні: загрожують
  | "accepted"                         // свідомо лишили (залишковий рівень)
  | "closed" | "materialized";         // вибули: не загрожують

const DEAD: ReadonlySet<State> = new Set(["closed", "materialized"]);

interface Risk {
  id: string;
  desc: string;
  p: number;       // ймовірність за горизонт, 0..1
  L: number;       // збиток, якщо вдарить (у грошах або днях)
  trigger: string; // спостережна ознака-тригер
  owner: string;   // жива людина з іменем, не «команда»
  state: State;
}

// Експозиція рядка — очікуваний збиток p·L, але лише поки рядок активний.
const exposure = (r: Risk): number =>
  DEAD.has(r.state) ? 0 : r.p * r.L;

// Сукупна експозиція портфеля — сума по всіх рядках (лінійність сподівання).
const portfolio = (reg: readonly Risk[]): number =>
  reg.reduce((sum, r) => sum + exposure(r), 0);
