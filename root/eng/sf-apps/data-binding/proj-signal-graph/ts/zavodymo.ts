// ── 4. Демонстрація ───────────────────────────────────────────────────
const s = signal(1), t = signal(10);
const c = { p: 0, q: 0, u: 0, r: 0, w: 0, e: 0 };

const p = computed(() => { c.p++; return s.get() * 2; });
const q = computed(() => { c.q++; return s.get() > 0; });
const u = computed(() => { c.u++; return t.get() + 1; });
const r = computed(() => { c.r++; return `${p.get()}${q.get() ? ' / так' : ' / ні'}`; });
const w = computed(() => { c.w++; return q.get() ? u.get() : 0; });

const stop = effect(() => { c.e++; console.log('r =', r.get()); });
w.get();          // перше читання й заводить w у граф (підписників у нього немає)

s.set(5);         // p, q, r, ефект — перераховано; w пропущено
t.set(20);        // тільки u і w; r та ефект не торкнуто взагалі
s.set(-3);        // q стало false → w пішло іншою гілкою й ВІДПУСТИЛО u
t.set(99);        // u перерахувалося — але вже ні для кого

console.log(c);   // { p: 3, q: 3, u: 3, r: 3, w: 3, e: 3 }
stop();
