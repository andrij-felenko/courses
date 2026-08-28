// «алгебра» — інтерфейс конструкторів, узагальнений за типом результату T:
interface ExprAlg<T> { lit(n: number): T; add(l: T, r: T): T; }

// терм — це функція над алгеброю, а не конкретне дерево:
const e = <T,>(a: ExprAlg<T>): T => a.add(a.lit(1), a.lit(2));

// нова ОПЕРАЦІЯ = нова реалізація алгебри; терм не чіпаємо:
const Eval:  ExprAlg<number> = { lit: n => n,        add: (l, r) => l + r };
const Print: ExprAlg<string> = { lit: n => `${n}`,   add: (l, r) => `(${l} + ${r})` };
e(Eval);   // 3
e(Print);  // "(1 + 2)"

// новий ТИП (варіант) = під-інтерфейс; старі терми лишаються валідні:
interface MulAlg<T> extends ExprAlg<T> { mul(l: T, r: T): T; }
