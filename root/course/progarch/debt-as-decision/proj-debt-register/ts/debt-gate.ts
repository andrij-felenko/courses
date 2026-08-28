// debt-gate.ts — журнал боргу як дані, що звіряються з кодом і метриками.
// Запуск у CI:  npx tsx debt-gate.ts   (ненульовий код виходу = білд червоний)

type State = "open" | "closed";
type Op = ">" | ">=" | "<" | "<=";

interface Clause { metric: string; op: Op; threshold: number; }  // машинний строк

interface Debt {
  id: string;          // ← ЗШИВАЧ: та сама мітка в коді (// DEBT(id)) і тут
  body: string;        // тіло боргу — що саме тимчасове
  why: string;         // чому взяли (дедлайн проти чесного рішення)
  seam: string;        // за яким швом замкнено (де його весь видно)
  interest: string;    // сигнал відсотка — куди дивитись, щоб побачити, як капає
  trigger: Clause[];   // ← СТРОК: будь-яка клауза істинна → час гасити
  repay: string;       // план погашення — чим заміняємо
  test: string;        // страховка — тест, що робить заміну безпечною
  owner: string;       // жива людина/команда; "" = діра
  state: State;
}
