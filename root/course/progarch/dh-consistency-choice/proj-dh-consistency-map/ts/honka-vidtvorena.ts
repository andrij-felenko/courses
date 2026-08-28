const A = new Replica("A·лідер"), B = new Replica("B·репліка"), E = new Replica("E·край");
const cluster = new Cluster([A, B, E], A, (to) => (to === B ? 1 : 5)); // E лагає вп'ятеро

const KEY = "grant:home-42:pidryadnyk";
cluster.write(KEY, true);          // власник видав доступ → версія 1
cluster.advance(10);               // усі копії наздогнали: A, B, E = v1(true)

// T0: власник ВІДКЛИКАЄ доступ.
cluster.write(KEY, false);         // → версія 2, лягає на A негайно
cluster.advance(2);                // 2 тики: B (лаг 1) уже має v2, E (лаг 5) — ще ні

// T1: підрядник тягне двері. Той самий факт, дві дороги читання.
// Навмисне беремо кворум БЕЗ лідера — {B, E} — і все одно ловимо відкликання.
console.log("строго {B,E}:", mayOpen(KEY, [B, E]) ? "ВІДЧИНИТИ" : "ВІДМОВА");
const stale = readEventual(KEY, E);
console.log("зрештою E:  ", stale?.value === true ? "ВІДЧИНИТИ" : "ВІДМОВА",
            `(версія ${stale?.version})`);

cluster.advance(4);                // E наздоганяє (лаг 5 від T0)
const now = readEventual(KEY, E);
console.log("зрештою E, збіжність:", now?.value === true ? "ВІДЧИНИТИ" : "ВІДМОВА",
            `(версія ${now?.version})`);
