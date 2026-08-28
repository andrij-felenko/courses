// ── 1. Стан рушія, вузол, стеження ────────────────────────────────────
type Eq<T> = (a: T, b: T) => boolean;

let epoch = 0;                          // номер поточного поширення
let frame: Derived<any> | null = null;  // вузол, який ЗАРАЗ обчислюється

abstract class Node {
  height = 0;        // 0 у джерела; у похідного — 1 + max(висот входів)
  changedAt = 0;     // епоха, у якій значення СПРАВДІ змінилося
  readonly subs = new Set<Derived<any>>();   // хто читає мене
}

/** Читання під час обчислення — це і є оголошення залежності. */
function track(n: Node): void {
  if (!frame) return;              // читання поза обчисленням нічого не підписує
  frame.deps.add(n);
  n.subs.add(frame);
}

// ── Джерело: єдине місце, куди пишуть ззовні ──────────────────────────
class Source<T> extends Node {
  constructor(private value: T, private eq: Eq<T> = Object.is) { super(); }

  get(): T { track(this); return this.value; }

  set(next: T): void {
    if (frame) throw new Error('запис у джерело зсередини обчислюваного вузла');
    if (this.eq(next, this.value)) return;   // відсічка: не змінилося — не сталося нічого
    this.value = next;
    this.changedAt = ++epoch;
    mark(this);                              // ФАЗА 1
    settleAll();                             // ФАЗА 2
  }
}
