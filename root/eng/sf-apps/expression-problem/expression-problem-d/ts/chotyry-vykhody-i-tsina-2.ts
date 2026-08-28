// «алгебра» — інтерфейс конструкторів, у якого тип продукту — параметр A
interface ExpAlg<A> {
  lit(n: number): A;
  add(a: A, b: A): A;
}
// операція = реалізація під носій A;  + операція — новий клас (СТОВПЕЦЬ задарма)
class Eval implements ExpAlg<number> {
  lit(n: number)            { return n; }
  add(a: number, b: number) { return a + b; }
}
class Print implements ExpAlg<string> {
  lit(n: number)            { return String(n); }
  add(a: string, b: string) { return `(${a}+${b})`; }
}
// + новий ВАРІАНТ mul = під-інтерфейс, старе ціле (РЯДОК задарма)
interface MulAlg<A> extends ExpAlg<A> { mul(a: A, b: A): A; }
