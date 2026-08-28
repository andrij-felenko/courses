T0, T1, M, S, L = 1, 2, 4, 8, 16          # біт = «функція ВИХОДИТЬ із цього класу»
ALL = T0 | T1 | M | S | L                 # 0b11111 = 31
WALLS = [(T0, "зберігає 0"), (T1, "зберігає 1"), (M, "монотонна"),
         (S, "самодвоїста"), (L, "лінійна")]


def zhegalkin(table):
    """Поліном Жегалкіна таблиці — перетворення Мебіуса на місці, O(n·2ⁿ)."""
    a = list(table)
    step = 1
    while step < len(a):
        for base in range(0, len(a), 2 * step):
            for j in range(base, base + step):
                a[j + step] ^= a[j]
        step *= 2
    return a


def escapes(table):
    """П'ятибітова маска втечі: які стіни пробиває ЦЯ функція."""
    last = len(table) - 1
    n = last.bit_length()                              # len(table) = 2ⁿ
    m = 0

    if table[0] != 0:                                  # f(0,…,0) ≠ 0
        m |= T0
    if table[last] != 1:                               # f(1,…,1) ≠ 1
        m |= T1
    if any(table[x] > table[x | 1 << k]                # ребро куба веде ВНИЗ
           for x in range(len(table))
           for k in range(n) if not x >> k & 1):
        m |= M
    if any(table[x] == table[last ^ x]                 # дзеркало десь збіглося
           for x in range(len(table))):
        m |= S
    if any(c and bin(mono).count("1") >= 2             # одночлен із добутком змінних
           for mono, c in enumerate(zhegalkin(table))):
        m |= L
    return m


def inspect(*tables):
    """Вердикт для набору + стіни, яких не пробив ніхто."""
    got = 0
    for t in tables:
        got |= escapes(t)
    return got == ALL, [name for bit, name in WALLS if not got & bit]


NOT, ZERO, ONE = [1, 0], [0, 0], [1, 1]
AND, OR, XOR = [0, 0, 0, 1], [0, 1, 1, 1], [0, 1, 1, 0]
IMPL, NAND, MAJ = [1, 0, 1, 1], [1, 1, 1, 0], [0, 0, 0, 1, 0, 1, 1, 1]

for name, fs in [("{NAND}", [NAND]), ("{¬, ∧}", [NOT, AND]), ("{∧, ∨}", [AND, OR]),
                 ("{⊕, ¬, 1}", [XOR, NOT, ONE]), ("{→}", [IMPL]),
                 ("{→, 0}", [IMPL, ZERO]), ("{¬, MAJ}", [NOT, MAJ])]:
    ok, left = inspect(*fs)
    print("%-11s %s" % (name, "ПОВНИЙ" if ok else
                        "не повний — ніхто не пробив: " + ", ".join(left)))

# усі 16 двовходових операцій: хто з них повний САМ-ОДИН?
solo = ["".join(str((code >> x) & 1) for x in range(4))
        for code in range(16)
        if escapes([(code >> x) & 1 for x in range(4)]) == ALL]
print("самодостатні серед 16 двовходових:", solo)
