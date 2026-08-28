/** Таблиця істинності: table[x] — значення на наборі x; біт k числа x — змінна xₖ. */
type Table = readonly (0 | 1)[];

const Wall = { T0: 1, T1: 2, M: 4, S: 8, L: 16 } as const;
const ALL = 0b11111;
const WALLS: ReadonlyArray<readonly [number, string]> = [
  [Wall.T0, "зберігає 0"], [Wall.T1, "зберігає 1"], [Wall.M, "монотонна"],
  [Wall.S, "самодвоїста"], [Wall.L, "лінійна"],
];

/** Поліном Жегалкіна — перетворення Мебіуса на місці, O(n·2ⁿ). */
function zhegalkin(table: Table): number[] {
  const a: number[] = [...table];
  for (let step = 1; step < a.length; step *= 2)
    for (let base = 0; base < a.length; base += 2 * step)
      for (let j = base; j < base + step; j++) a[j + step] ^= a[j];
  return a;
}

const popcount = (m: number): number => { let c = 0; for (; m; m &= m - 1) c++; return c; };

/** П'ятибітова маска втечі: які стіни пробиває ЦЯ функція. */
function escapes(table: Table): number {
  const last = table.length - 1;
  const n = 32 - Math.clz32(last);                    // table.length = 2ⁿ
  let m = 0;

  if (table[0] !== 0) m |= Wall.T0;                   // f(0,…,0) ≠ 0
  if (table[last] !== 1) m |= Wall.T1;                // f(1,…,1) ≠ 1

  for (let x = 0; x <= last; x++)                     // ребро куба веде ВНИЗ
    for (let k = 0; k < n; k++)
      if (!((x >> k) & 1) && table[x] > table[x | (1 << k)]) m |= Wall.M;

  for (let x = 0; x <= last; x++)                     // дзеркало десь збіглося
    if (table[x] === table[last ^ x]) m |= Wall.S;

  zhegalkin(table).forEach((c, mono) => {             // одночлен із добутком
    if (c && popcount(mono) >= 2) m |= Wall.L;
  });
  return m;
}

interface Verdict {
  readonly complete: boolean;
  readonly unbroken: readonly string[];               // стіни, яких не пробив ніхто
}

function inspect(...tables: Table[]): Verdict {
  const got = tables.reduce((acc, t) => acc | escapes(t), 0);
  return {
    complete: got === ALL,
    unbroken: WALLS.filter(([bit]) => !(got & bit)).map(([, name]) => name),
  };
}

const NOT: Table = [1, 0], ZERO: Table = [0, 0], ONE: Table = [1, 1];
const AND: Table = [0, 0, 0, 1], OR: Table = [0, 1, 1, 1], XOR: Table = [0, 1, 1, 0];
const IMPL: Table = [1, 0, 1, 1], NAND: Table = [1, 1, 1, 0];
const MAJ: Table = [0, 0, 0, 1, 0, 1, 1, 1];

const cases: ReadonlyArray<readonly [string, Table[]]> = [
  ["{NAND}", [NAND]], ["{¬, ∧}", [NOT, AND]], ["{∧, ∨}", [AND, OR]],
  ["{⊕, ¬, 1}", [XOR, NOT, ONE]], ["{→}", [IMPL]],
  ["{→, 0}", [IMPL, ZERO]], ["{¬, MAJ}", [NOT, MAJ]],
];

for (const [name, fs] of cases) {
  const { complete, unbroken } = inspect(...fs);
  console.log(name.padEnd(11),
    complete ? "ПОВНИЙ" : `не повний — ніхто не пробив: ${unbroken.join(", ")}`);
}
