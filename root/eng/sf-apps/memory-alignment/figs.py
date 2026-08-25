# -*- coding: utf-8 -*-
"""Фігури до теми «Вирівнювання даних у пам'яті» (memory alignment).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

RED_BG   = "#fdecea"   # число / «гаряче» / небезпека
BLUE_BG  = "#eaf0fd"   # холодне
GREEN_BG = "#eaf6ee"   # добре / висновок
AMBER    = "#b8860b"
AMBER_BG = "#fdf6e3"
PAD_BG   = "#e9ecef"   # байти-заповнювачі (падінг) — «повітря»
CELL_BG  = "#f3f5f8"
MONO     = "Consolas, 'DejaVu Sans Mono', monospace"


def out(name, *a, **k):
    render(os.path.join(IMG, name), *a, **k)


def mono(x, y, s, size=13, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


# ── 1. Чому шина хоче вирівняних адрес ────────────────────────────────────────
def fig_why_aligned():
    W, H = 900, 500
    f = []
    x0, y = 70, 92
    bw = 26   # ширина одного байта

    # верхня стрічка: сітка байтів, згрупована в комірки по 4
    f.append(text(x0, y - 14, "пам'ять як 4-байтні комірки шини:", size=12.5, color=INK, anchor="start", bold=True))
    for c in range(4):
        cx = x0 + c * 4 * bw
        f.append(rect(cx, y, 4 * bw, 40, fill=CELL_BG, stroke=INK, sw=2, rx=5))
        f.append(text(cx + 2 * bw, y + 58, "комірка %d…%d" % (c * 4, c * 4 + 3), size=10, color=MUTED))
        for b in range(4):
            f.append(mono(cx + b * bw + bw / 2, y + 25, str(c * 4 + b), size=10, color=MUTED, anchor="middle"))
            if b:
                f.append(line(cx + b * bw, y + 4, cx + b * bw, y + 36, color="#c7ccd1", sw=1))
    f.append(text(x0 - 6, y + 25, "адр.", size=10, color=MUTED, anchor="end"))

    # ── ЛІВОРУЧ (умовно вгорі): вирівняне число за адресою 4 ──
    yA = 210
    f.append(rect(60, yA - 34, 780, 96, fill=GREEN_BG, stroke=FIELD, sw=1.6, rx=10))
    f.append(text(76, yA - 14, "✓ ВИРІВНЯНЕ: int32 за адресою 4 (4 кратне 4)", size=13, color=FIELD, anchor="start", bold=True))
    for c in range(4):
        cx = x0 + c * 4 * bw
        f.append(rect(cx, yA, 4 * bw, 34, fill=BG, stroke=INK, sw=1.4, rx=4))
    # число займає байти 4..7 = комірка 1
    f.append(rect(x0 + 4 * bw, yA, 4 * bw, 34, fill=RED_BG, stroke=POS, sw=2.2, rx=4))
    f.append(mono(x0 + 6 * bw, yA + 22, "int32", size=13, color=POS, anchor="middle", bold=True))
    f.append(text(x0 + 6 * bw, yA + 52, "одне звертання до шини", size=11, color=FIELD, bold=True))

    # ── ПРАВОРУЧ (умовно нижче): невирівняне число за адресою 6 ──
    yB = 350
    f.append(rect(60, yB - 34, 780, 120, fill=RED_BG, stroke=POS, sw=1.6, rx=10))
    f.append(text(76, yB - 14, "✗ НЕВИРІВНЯНЕ: int32 за адресою 6 (6 НЕ кратне 4)", size=13, color=POS, anchor="start", bold=True))
    for c in range(4):
        cx = x0 + c * 4 * bw
        f.append(rect(cx, yB, 4 * bw, 34, fill=BG, stroke=INK, sw=1.4, rx=4))
    # число займає байти 6..9 — верхи на межі комірок 1 і 2
    f.append(rect(x0 + 6 * bw, yB, 4 * bw, 34, fill="#f7c9c0", stroke=POS, sw=2.2, rx=4))
    f.append(mono(x0 + 8 * bw, yB + 22, "int32", size=13, color=POS, anchor="middle", bold=True))
    # позначки двох читань
    f.append(line(x0 + 4 * bw, yB + 46, x0 + 8 * bw, yB + 46, color=NEG, sw=2))
    f.append(text(x0 + 6 * bw, yB + 62, "читання 1 (комірка 4…7)", size=10, color=NEG, bold=True))
    f.append(line(x0 + 8 * bw, yB + 66, x0 + 12 * bw, yB + 66, color=NEG, sw=2))
    f.append(text(x0 + 10 * bw, yB + 82, "читання 2 (комірка 8…11)", size=10, color=NEG, bold=True))

    f.append(text(W / 2, 486,
                  "Вирівняне число — цілком в одній комірці (1 доступ). Невирівняне «сидить верхи» на межі → 2 доступи + склеювання.",
                  size=11.5, color=INK, bold=True))
    out("why-aligned.svg", W, H, *f,
        title="Чому шина хоче вирівняних адрес")


# ── 2. Два світи реакції на невирівняний доступ ───────────────────────────────
def fig_two_worlds():
    W, H = 900, 470
    f = []
    # ліва панель: терпить
    f.append(rect(60, 80, 380, 320, fill=GREEN_BG, stroke=FIELD, sw=1.8, rx=12))
    f.append(text(250, 108, "Терпить (повільніше)", size=15, color=FIELD, bold=True))
    f.append(text(250, 130, "x86 / x86-64 · Cortex-M3/M4/M7", size=11.5, color=INK))
    items_ok = [
        ("Доступ дозволено", "процесор сам робить 2 читання + склеювання"),
        ("Код просто працює", "програміст навіть не помічає"),
        ("Плата — швидкодія", "і то помітно лише на розколі рядка кешу"),
        ("Сучасні x86 (від Nehalem)", "усередині рядка кешу — майже без втрат"),
    ]
    yy = 160
    for head, sub in items_ok:
        f.append(text(80, yy, "•  " + head, size=12.5, color=INK, anchor="start", bold=True))
        f.append(text(96, yy + 18, sub, size=10, color=MUTED, anchor="start"))
        yy += 58
    # права панель: падає
    f.append(rect(460, 80, 380, 320, fill=RED_BG, stroke=POS, sw=1.8, rx=12))
    f.append(text(650, 108, "Падає (HardFault)", size=15, color=POS, bold=True))
    f.append(text(650, 130, "Cortex-M0/M0+ · DEC Alpha · периферія", size=11.5, color=INK))
    items_bad = [
        ("Апаратура не вміє", "невирівняного доступу до слова/півслова"),
        ("Миттєвий виняток", "LDR/STR з невирівняною адресою → fault"),
        ("Прошивка у HardFault", "зависання чи перезавантаження"),
        ("Завжди faultять", "LDM/STM, LDRD, атомарні, доступ до периферії"),
    ]
    yy = 160
    for head, sub in items_bad:
        f.append(text(480, yy, "•  " + head, size=12.5, color=INK, anchor="start", bold=True))
        f.append(text(496, yy + 18, sub, size=10, color=MUTED, anchor="start"))
        yy += 58
    f.append(rect(60, 414, 780, 44, fill=AMBER_BG, stroke=AMBER, sw=1.6, rx=10))
    f.append(text(W / 2, 436,
                  "Той самий рядок C: на ПК тихо повільний, на Cortex-M0 — мертвий пристрій. «Працює в мене на ноуті» нічого не доводить.",
                  size=11.5, color=INK, bold=True))
    f.append(text(W / 2, 452, "Біт CCR.UNALIGN_TRP на M3+ можна ввімкнути й змусити faultити всюди — для налагодження.",
                  size=10, color=MUTED, italic=True))
    out("two-worlds.svg", W, H, *f,
        title="Невирівняний доступ: терпіти повільно чи впасти в HardFault")


# ── 3. Падінг у структурі ─────────────────────────────────────────────────────
def fig_struct_padding():
    W, H = 940, 480
    f = []
    bw = 58
    x0 = 90

    def cell(i, label, col, bg, sub=None):
        x = x0 + i * bw
        f.append(rect(x, 150, bw, 46, fill=bg, stroke=col, sw=2, rx=5))
        f.append(text(x + bw / 2, 178, label, size=13, color=col, bold=True))
        f.append(mono(x + bw / 2, 138, str(i), size=10, color=MUTED, anchor="middle"))
        if sub:
            f.append(text(x + bw / 2, 214, sub, size=9.5, color=MUTED))

    f.append(text(x0, 118, "struct Bad { uint8_t flag; uint32_t value; uint16_t count; };   →   sizeof == 12",
                  size=13.5, color=INK, anchor="start", bold=True))
    # зсуви 0..11
    cell(0, "flag", POS, RED_BG, "1 байт")
    for i in (1, 2, 3):
        cell(i, "pad", MUTED, PAD_BG)
    for i in (4, 5, 6, 7):
        cell(i, "value", NEG, BLUE_BG)
    for i in (8, 9):
        cell(i, "count", FIELD, GREEN_BG)
    for i in (10, 11):
        cell(i, "pad", MUTED, PAD_BG)
    # дужки-пояснення
    f.append(text(x0 + 2 * bw, 250, "3 байти падінгу:", size=11, color=INK, bold=True))
    f.append(text(x0 + 2 * bw, 267, "щоб value лягло", size=10, color=MUTED))
    f.append(text(x0 + 2 * bw, 281, "на зсув 4 (кратно 4)", size=10, color=MUTED))
    f.append(text(x0 + 10.5 * bw, 250, "хвостовий падінг:", size=11, color=INK, bold=True))
    f.append(text(x0 + 10.5 * bw, 267, "розмір → кратний 4,", size=10, color=MUTED))
    f.append(text(x0 + 10.5 * bw, 281, "щоб arr[1] почався рівно", size=10, color=MUTED))
    f.append(text(x0 + 5.5 * bw, 250, "value @ зсув 4 ✓", size=11, color=NEG, bold=True))

    # легенда
    f.append(rect(x0, 306, 16, 16, fill=PAD_BG, stroke=MUTED, sw=1.4, rx=3))
    f.append(text(x0 + 24, 319, "= падінг (невидимі байти-заповнювачі, «повітря»): 5 із 12 байтів",
                  size=11, color=INK, anchor="start"))

    # порівняння Good
    f.append(rect(60, 344, 820, 108, fill=GREEN_BG, stroke=FIELD, sw=1.7, rx=12))
    f.append(text(80, 368, "Перегрупуй від більших полів до менших → падінг стискається:", size=12.5, color=FIELD, anchor="start", bold=True))
    good = [("value", NEG, BLUE_BG, 4), ("count", FIELD, "#d8f0e0", 2), ("flag", POS, RED_BG, 1), ("pad", MUTED, PAD_BG, 1)]
    gx = 90
    gbw = 42
    off = 0
    for label, col, bg, span in good:
        for _ in range(span):
            f.append(rect(gx, 396, gbw, 34, fill=bg, stroke=col, sw=1.8, rx=4))
            f.append(mono(gx + gbw / 2, 388, str(off), size=9, color=MUTED, anchor="middle"))
            gx += gbw
            off += 1
        f.append(text(gx - span * gbw / 2 - gbw / 2 + gbw / 2, 419,
                      label if label != "pad" else "pad", size=10,
                      color=col, bold=(label != "pad")))
    f.append(text(560, 410, "struct Good → sizeof == 8", size=15, color=FIELD, anchor="start", bold=True))
    f.append(text(560, 432, "ті самі 3 поля — на третину менше пам'яті", size=11, color=MUTED, anchor="start", italic=True))
    out("struct-padding.svg", W, H, *f,
        title="Падінг у структурі: чому sizeof більший за суму полів")


# ── 4. Атомарність від вирівнювання ───────────────────────────────────────────
def fig_atomicity():
    W, H = 900, 470
    f = []
    bw = 28
    # ── ЛІВОРУЧ: вирівняне — неподільно ──
    f.append(rect(60, 84, 380, 300, fill=GREEN_BG, stroke=FIELD, sw=1.8, rx=12))
    f.append(text(250, 110, "✓ Вирівняне — атомарне", size=14.5, color=FIELD, bold=True))
    lx = 96
    ly = 150
    for c in range(2):
        f.append(rect(lx + c * 4 * bw, ly, 4 * bw, 36, fill=BG, stroke=INK, sw=1.4, rx=4))
    f.append(rect(lx, ly, 4 * bw, 36, fill=RED_BG, stroke=POS, sw=2.2, rx=4))
    f.append(mono(lx + 2 * bw, ly + 24, "uint32", size=12.5, color=POS, anchor="middle", bold=True))
    f.append(text(lx + 2 * bw, ly - 8, "одна комірка", size=10, color=MUTED))
    f.append(text(lx + 6 * bw, ly + 24, "сусідня", size=10, color=MUTED, anchor="middle"))
    f.append(rect(80, 226, 340, 66, fill=BG, stroke=FIELD, sw=1.5, rx=8))
    f.append(text(250, 248, "оновлення = 1 неподільна операція", size=12, color=INK, bold=True))
    f.append(text(250, 270, "читач бачить або старе, або нове —", size=11, color=MUTED))
    f.append(text(250, 285, "ніколи проміжне", size=11, color=MUTED))
    f.append(text(250, 330, "Можна безпечно ділити між", size=11.5, color=FIELD, bold=True))
    f.append(text(250, 348, "перериванням і кодом, між ядрами", size=11.5, color=FIELD, bold=True))

    # ── ПРАВОРУЧ: невирівняне — розірване ──
    f.append(rect(460, 84, 380, 300, fill=RED_BG, stroke=POS, sw=1.8, rx=12))
    f.append(text(650, 110, "✗ Невирівняне — розірване", size=14.5, color=POS, bold=True))
    rx0 = 496
    for c in range(2):
        f.append(rect(rx0 + c * 4 * bw, ly, 4 * bw, 36, fill=BG, stroke=INK, sw=1.4, rx=4))
    # число верхи на межі: байти 2..5 (зсув 2 у комірці)
    f.append(rect(rx0 + 2 * bw, ly, 4 * bw, 36, fill="#f7c9c0", stroke=POS, sw=2.2, rx=4))
    f.append(mono(rx0 + 4 * bw, ly + 24, "uint32", size=12.5, color=POS, anchor="middle", bold=True))
    f.append(line(rx0, ly + 48, rx0 + 4 * bw, ly + 48, color=NEG, sw=2))
    f.append(text(rx0 + 2 * bw, ly + 63, "запис 1", size=10, color=NEG, bold=True))
    f.append(line(rx0 + 4 * bw, ly + 48, rx0 + 8 * bw, ly + 48, color=NEG, sw=2))
    f.append(text(rx0 + 6 * bw, ly + 63, "запис 2", size=10, color=NEG, bold=True))
    f.append(rect(480, 250, 340, 76, fill=BG, stroke=POS, sw=1.5, rx=8))
    f.append(text(650, 272, "запис = 2 операції; між ними", size=12, color=INK, bold=True))
    f.append(text(650, 292, "встромляється інший виконавець →", size=11, color=MUTED))
    f.append(text(650, 308, "бачить половину нову, половину стару", size=11, color=POS, bold=True))
    f.append(text(650, 350, "розірваний доступ (torn read/write)", size=11.5, color=POS, bold=True, italic=True))

    f.append(rect(60, 400, 780, 52, fill=AMBER_BG, stroke=AMBER, sw=1.6, rx=10))
    f.append(text(W / 2, 422, "Ділиш змінну між виконавцями (переривання, ядра) — тримай її ВИРІВНЯНОЮ, інакше атомарність зникає.",
                  size=11.5, color=INK, bold=True))
    f.append(text(W / 2, 442, "Деякі ARMv7 навіть вирівняний 64-бітний доступ роблять двома 32-бітними записами — не покладайся наосліп.",
                  size=10, color=MUTED, italic=True))
    out("atomicity.svg", W, H, *f,
        title="Атомарність тримається на вирівнюванні")


# ── 5. Спектр «релігії вирівнювання» крізь епохи ─────────────────────────────
def fig_alignment_spectrum():
    """Історична карта: хто faultить, хто емулює, хто терпить — і як хитнулося з роками."""
    W, H = 960, 470
    f = []

    # три вертикальні смуги-табори
    colw = 296
    gap = 12
    x0 = 24
    ytop = 70
    ph = 330

    camps = [
        (POS,  RED_BG,  "СУВОРО: апаратний виняток",
         "невирівняний доступ = fault; крапка",
         ["DEC Alpha (1992) — слова/quadword;", "  байтів узагалі нема до BWX (1996)",
          "MIPS, SPARC — fault за замовч.", "Motorola 68000/68010 — address error",
          "ARM Cortex-M0/M0+ (ARMv6-M)"]),
        (AMBER, AMBER_BG, "ЕМУЛЮЄ: тихо, але поволі",
         "ядро ловить trap, збирає число, вертає",
         ["DEC Alpha + ОС: trap у ядро,", "  аж ~тисячі тактів на доступ",
          "RISC-V — на розсуд реалізації:", "  або залізо, або trap-handler",
          "Linux на суворих ISA — те саме"]),
        (FIELD, GREEN_BG, "ТЕРПИТЬ: залізо збирає само",
         "подвійне читання в кремнії; платиш швидкодією",
         ["x86 / x86-64 — від 8086 (1978)", "Motorola 68020 (1984) — зняв заборону",
          "ARMv6+ / Cortex-M3, M4, M7", "PowerPC — 32-біт так, 64-біт fault",
          "AArch64 — звичайні load/store"]),
    ]

    for i, (col, bg, head, sub, rows) in enumerate(camps):
        x = x0 + i * (colw + gap)
        f.append(rect(x, ytop, colw, ph, fill=bg, stroke=col, sw=2, rx=12))
        f.append(text(x + colw / 2, ytop + 26, head, size=13.5, color=col, bold=True))
        f.append(text(x + colw / 2, ytop + 46, sub, size=10, color=MUTED, italic=True))
        f.append(line(x + 18, ytop + 58, x + colw - 18, ytop + 58, color=col, sw=1))
        yy = ytop + 84
        for r in rows:
            indent = 30 if r.startswith("  ") else 18
            f.append(text(x + indent, yy, r.strip() if r.startswith("  ") else r,
                          size=11, color=INK, anchor="start"))
            yy += 22

    # стрілка «з роками кремній подешевшав — маятник хитнувся до терпимості»
    ay = ytop + ph + 34
    f.append(arrow(x0 + 40, ay, x0 + 3 * colw + 2 * gap - 40, ay, color=NEG, sw=2.4))
    f.append(text(W / 2, ay - 12, "з роками транзистори подешевшали → маятник хитнувся від суворості до терпимості",
                  size=11.5, color=NEG, bold=True))
    f.append(text(x0 + 40, ay + 20, "1980-ті: «декодер має бути простий»", size=10, color=MUTED, anchor="start"))
    f.append(text(x0 + 3 * colw + 2 * gap - 40, ay + 20, "2000-ні+: «клади куди хочеш»", size=10, color=MUTED, anchor="end"))

    out("alignment-spectrum.svg", W, H, *f,
        title="Вирівнювання як апаратна релігія: три табори крізь епохи")


if __name__ == "__main__":
    fig_why_aligned()
    fig_two_worlds()
    fig_struct_padding()
    fig_atomicity()
    fig_alignment_spectrum()
    print("OK: 5 фігур у", IMG)
