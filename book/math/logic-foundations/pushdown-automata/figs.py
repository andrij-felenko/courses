# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Магазинні автомати».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

MARK  = "#2457d6"   # клітина-лічильник X на стеку (холодний синій)
BOTTOM= "#9aa3ad"   # дно магазина Z₀
GREEN = "#27ae60"   # прийом / порожній стек
RED   = "#c0392b"   # акцент
STFILL= "#eef2fb"   # заливка керування/стану
BOTFIL= "#eef0f2"   # заливка дна
MARKF = "#dfe7fb"   # заливка клітини X


def stack_col(cx, base_y, cells, cw=48, ch=28):
    """Стек-стовпчик: cells — список знизу вгору, кожен (label, fill, stroke)."""
    out = []
    for i, (lab, fill, stroke) in enumerate(cells):
        y = base_y - (i + 1) * ch
        out.append(rect(cx - cw / 2, y, cw, ch, fill=fill, stroke=stroke, sw=1.6, rx=3))
        out.append(text(cx, y + ch / 2 + 5, lab, size=14, color=INK, bold=True))
    return "".join(out)


# ── Фігура 1: стек у дії на мові aⁿbⁿ (n=3, вхід «aaabbb») ────────────────────
# Серце статті: кладемо X на кожне a, знімаємо на кожне b; порожній стек = прийом.
# Сім знімків стека вздовж прогону — видно ріст і спад, і рівність = баланс.
def fig_stack_run():
    W, H = 980, 430
    P = []
    P.append(text(W / 2, 40, "Вхід  a a a b b b  —  мова aⁿbⁿ (тут n = 3)", size=16, color=INK, bold=True))
    P.append(text(W / 2, 62, "на кожне a кладемо X, на кожне b знімаємо X; наприкінці стек порожній → баланс, прийом",
                  size=11.5, color=MUTED))

    xs = [90, 220, 350, 480, 610, 740, 870]
    base_y = 350
    Z = ("Z", BOTFIL, BOTTOM)
    X = ("X", MARKF, MARK)
    snaps = [
        [Z],                     # старт
        [Z, X],                  # a
        [Z, X, X],               # a
        [Z, X, X, X],            # a
        [Z, X, X],               # b
        [Z, X],                  # b
        [Z],                     # b → порожньо
    ]
    labs = ["старт", "a → push", "a → push", "a → push", "b → pop", "b → pop", "b → pop"]

    # спільна «підлога»
    P.append(line(60, base_y, 910, base_y, color="#cfd4da", sw=1.6))
    # фази
    P.append(text((xs[1] + xs[3]) / 2, 92, "фаза a: стек росте", size=12, color=MARK, bold=True))
    P.append(text((xs[4] + xs[6]) / 2, 92, "фаза b: стек спадає", size=12, color=RED, bold=True))
    P.append(line(xs[1] - 30, 100, xs[3] + 30, 100, color=MARK, sw=1.4))
    P.append(line(xs[4] - 30, 100, xs[6] + 30, 100, color=RED, sw=1.4))

    for x, snap, lab in zip(xs, snaps, labs):
        P.append(stack_col(x, base_y, snap))
        P.append(text(x, base_y + 22, lab, size=11.5, color=INK))

    # прийом під останнім
    P.append(text(xs[6], base_y + 44, "стек порожній ✓", size=12, color=GREEN, bold=True))
    render("img/stack-run.svg", W, H, *P)


# ── Фігура 2: модель магазинного автомата (керування + стрічка + стек) ────────
# Анатомія: скінченне керування (як у СА) + одностороння стрічка входу + СТЕК —
# нова, необмежена, але LIFO-пам'ять. Внизу — форма переходу δ.
def fig_machine_model():
    W, H = 880, 470
    P = []
    P.append(text(W / 2, 34, "Магазинний автомат = скінченне керування + стек", size=16, color=INK, bold=True))

    # ── стрічка входу (зверху, лише читання, лише вперед) ──
    tape_x, tape_y, cw = 150, 78, 52
    syms = ["a", "a", "b", "b", "⊔"]
    for i, s in enumerate(syms):
        x = tape_x + i * cw
        fill = "#fbfbfb" if s != "⊔" else "#f1f1f1"
        P.append(rect(x, tape_y, cw, 40, fill=fill, stroke="#c9ced4", sw=1.4, rx=3))
        P.append(text(x + cw / 2, tape_y + 26, s, size=16, color=INK, bold=(s != "⊔")))
    P.append(text(tape_x, tape_y - 12, "стрічка входу — читаємо ліворуч-праворуч, лише вперед, без запису",
                  size=11, color=MUTED, anchor="start"))
    # головка читання
    head_x = tape_x + 2 * cw + cw / 2
    P.append(arrow(head_x, 168, head_x, tape_y + 44, color=INK, sw=2))
    P.append(text(head_x + 8, 158, "головка", size=10.5, color=MUTED, anchor="start"))

    # ── скінченне керування (центр) ──
    cbx, cby, cbw, cbh = 130, 200, 240, 96
    P.append(rect(cbx, cby, cbw, cbh, fill=STFILL, stroke=INK, sw=2, rx=10))
    P.append(text(cbx + cbw / 2, cby + 34, "Скінченне керування", size=14, color=INK, bold=True))
    P.append(text(cbx + cbw / 2, cby + 58, "стани Q · функція δ", size=12, color=MUTED))
    P.append(text(cbx + cbw / 2, cby + 78, "(як у скінченного автомата)", size=10.5, color=MUTED))

    # ── стек (праворуч, вертикальний, доступ лише з вершини) ──
    sx = 640
    base_y = 340
    cells = [("Z₀", BOTFIL, BOTTOM), ("X", MARKF, MARK), ("X", MARKF, MARK)]
    P.append(stack_col(sx, base_y, cells, cw=64, ch=32))
    P.append(line(sx - 40, base_y, sx + 40, base_y, color="#cfd4da", sw=1.6))
    P.append(text(sx, base_y + 22, "стек (магазин)", size=12, color=INK, bold=True))
    P.append(text(sx, base_y + 40, "необмежений, але лише LIFO", size=10.5, color=MUTED))
    P.append(text(sx, base_y - 3 * 32 - 14, "вершина", size=11, color=MARK, bold=True))
    # push/pop подвійна стрілка збоку від вершини
    P.append(arrow(sx + 60, base_y - 2 * 32, sx + 60, base_y - 3 * 32 - 6, color=MARK, sw=1.8))
    P.append(arrow(sx + 84, base_y - 3 * 32 - 6, sx + 84, base_y - 2 * 32, color=MARK, sw=1.8))
    P.append(text(sx + 74, base_y - 3 * 32 - 16, "push / pop", size=10.5, color=MARK, anchor="middle"))

    # зв'язок керування ↔ стек (читає вершину, пише вершину)
    P.append(arrow(cbx + cbw, cby + cbh / 2 - 8, sx - 40, base_y - 2 * 32 - 8, color=INK, sw=1.8))
    P.append(arrow(sx - 44, base_y - 32, cbx + cbw + 4, cby + cbh / 2 + 22, color=INK, sw=1.8))
    P.append(text((cbx + cbw + sx) / 2 + 6, 250, "бачить вершину", size=10.5, color=MUTED))
    P.append(text((cbx + cbw + sx) / 2 + 6, 322, "змінює вершину", size=10.5, color=MUTED))

    # ── форма переходу δ (внизу) ──
    by = 408
    P.append(rect(130, by, 620, 46, fill="#f6f8fb", stroke="#d6dde8", sw=1.5, rx=8))
    P.append(text(150, by + 28, "δ( q , a або ε , X )  →  ( q′ , γ )",
                  size=15, color=INK, anchor="start", bold=True))
    P.append(text(470, by + 20, "стан і вершина X кажуть, куди йти", size=10.5, color=MUTED, anchor="start"))
    P.append(text(470, by + 36, "і чим замінити X на стеку (рядок γ)", size=10.5, color=MUTED, anchor="start"))
    render("img/machine-model.svg", W, H, *P)


# ── Фігура 3: ієрархія Хомського — де сидить магазинний автомат ───────────────
# Вкладені кільця: регулярні ⊂ контекстно-вільні ⊂ контекстно-залежні ⊂
# рекурсивно-перелічні; для кожного — своя машина й приклад мови. Магазинний
# автомат = друга сходинка, підсвічена; стек додає рівно одну вкладеність.
def fig_hierarchy():
    W, H = 820, 520
    P = []
    P.append(text(W / 2, 34, "Де сидить магазинний автомат: ієрархія Хомського", size=16, color=INK, bold=True))

    # вкладені прямокутники (симетричний вступ 60 по кожній стороні)
    boxes = [
        (70, 66, 680, 424, "#ffffff", "#b9c0c9"),   # RE
        (130, 126, 560, 304, "#fcfcfd", "#aeb6c0"),  # CS
        (190, 186, 440, 184, "#eafaf0", GREEN),      # CF (наша)
        (250, 246, 320, 64, "#f4f7fc", "#8aa0c8"),   # Reg (найглибша)
    ]
    for x, y, w, h, fill, stroke in boxes:
        sw = 2.4 if stroke == GREEN else 1.6
        P.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=10))

    cx = W / 2
    # підписи у верхніх смугах кілець (по дві лінії, не перетинаються — 60px крок)
    P.append(text(cx, 92, "Рекурсивно-перелічні", size=13.5, color=INK, bold=True))
    P.append(text(cx, 110, "машина Тюринга — «чи зупиниться програма»", size=11, color=MUTED))

    P.append(text(cx, 152, "Контекстно-залежні", size=13.5, color=INK, bold=True))
    P.append(text(cx, 170, "лінійно-обмежений автомат — aⁿbⁿcⁿ", size=11, color=MUTED))

    P.append(text(cx, 212, "Контекстно-вільні — МАГАЗИННИЙ автомат", size=13.5, color=GREEN, bold=True))
    P.append(text(cx, 230, "aⁿbⁿ · збалансовані дужки · арифметичні вирази", size=11, color="#1e7a45"))

    P.append(text(cx, 272, "Регулярні", size=13, color=INK, bold=True))
    P.append(text(cx, 290, "скінченний автомат — (ab)*", size=11, color=MUTED))

    # підсумковий рядок під кільцями
    P.append(text(cx, 470, "Кожне кільце додає рівно ту пам'ять, що піднімає на сходинку:", size=12, color=INK))
    P.append(text(cx, 490, "стек дає одну вкладеність — між скінченним автоматом і машиною Тюринга.", size=12, color=INK))
    render("img/hierarchy.svg", W, H, *P)


# ══════════════════════════════════════════════════════════════════════════════
# Фігури до вставки proj-expression-parser.md — розбір арифметичного виразу
# ══════════════════════════════════════════════════════════════════════════════

OPS   = "#c0392b"   # стек операторів (гарячий — те, що ЧЕКАЄ)
OPSF  = "#fdecea"
VALS  = "#2457d6"   # стек значень (холодний — те, що вже пораховано)
VALSF = "#e9eefb"
BARR  = "#8a6d1f"   # бар'єр «(»
BARRF = "#fdf4dd"


def _col(cx, base_y, cells, cw=56, ch=30, size=14):
    """Стовпчик-стек знизу вгору: cells — [(label, fill, stroke)]."""
    out = []
    for i, (lab, fill, stroke) in enumerate(cells):
        y = base_y - (i + 1) * ch
        out.append(fitbox(cx - cw / 2, y, cw, ch, lab, size=size,
                          fill=fill, stroke=stroke, sw=1.6, rx=3, bold=True))
    return "".join(out)


# ── Фігура 4: коли відкладений оператор спрацьовує ────────────────────────────
# Серце сортувальної станції: два майже однакові вирази, різна доля оператора.
# Ліворуч наступний СИЛЬНІШИЙ → попередній чекає (стек росте).
# Праворуч наступний НЕ сильніший → попередній спрацьовує негайно.
def fig_precedence_defer():
    W, H = 1020, 560
    P = []
    P.append(text(W / 2, 38, "Коли відкладений оператор нарешті спрацьовує", size=17, color=INK, bold=True))
    P.append(text(W / 2, 62, "два вирази з тих самих чотирьох лексем — і протилежна доля першого оператора",
                  size=12, color=MUTED))

    panels = [
        # (центр, вираз, момент, порівняння, вердикт, колір вердикту,
        #  клітини стека знизу вгору, розв'язка, підсумок)
        (265, "2 + 3 * 4", "читаємо *  —  на стеку чекає +",
         "пріоритет( * ) = 2   >   пріоритет( + ) = 1",
         "сильніше → + ЧЕКАЄ далі, кладемо * зверху", OPS,
         [("+", OPSF, OPS), ("*", OPSF, OPS)],
         ["наприкінці знімаємо зверху вниз:", "спершу 3 * 4 = 12,   тоді 2 + 12 = 14"], "2 + 3 * 4  =  14"),
        (755, "2 * 3 + 4", "читаємо +  —  на стеку чекає *",
         "пріоритет( + ) = 1   ≤   пріоритет( * ) = 2",
         "не сильніше → * СПРАЦЬОВУЄ негайно: 2 * 3 = 6", VALS,
         [("+", OPSF, OPS)],
         ["* уже зійшов зі стека,", "лишилося 6 + 4 = 10"], "2 * 3 + 4  =  10"),
    ]

    for cx, expr, moment, cmp_, verdict, vcol, cells, tail, total in panels:
        x0 = cx - 220
        P.append(rect(x0, 88, 440, 424, fill="#fcfdfe", stroke="#dfe4ea", sw=1.5, rx=10))
        P.append(text(cx, 124, expr, size=24, color=INK, bold=True))
        P.append(text(cx, 154, moment, size=12.5, color=MUTED))
        P.append(fitbox(x0 + 24, 172, 392, 34, cmp_, size=13.5,
                        fill="#f4f6f8", stroke="#cfd6df", sw=1.4, rx=6))
        P.append(fitbox(x0 + 24, 216, 392, 34, verdict, size=12.5,
                        fill="#ffffff", stroke=vcol, sw=1.8, rx=6, color=vcol, bold=True))

        base_y = 400
        P.append(line(cx - 70, base_y, cx + 70, base_y, color="#cfd4da", sw=1.6))
        P.append(_col(cx, base_y, cells))
        P.append(text(cx, base_y + 22, "стек операторів", size=11.5, color=MUTED))

        P.append(mtext(cx, base_y + 52, tail, size=12, color=INK, lh=1.35))
        P.append(text(cx, 502, total, size=15, color=INK, bold=True))

    render("img/precedence-defer.svg", W, H, *P)


# ── Фігура 5: повний прогін «2*(3+4)-1» на двох стеках ────────────────────────
# Покроково: що робить машина на кожній лексемі й як стоять обидва стеки.
# Видно два цікаві місця — «)» згортає до бар'єра, «−» витісняє сильніше «*».
def fig_expr_trace():
    W, H = 1040, 560
    P = []
    P.append(text(W / 2, 38, "Прогін виразу  2 * ( 3 + 4 ) − 1  на двох стеках", size=17, color=INK, bold=True))
    P.append(text(W / 2, 62, "лексему прочитали — машина або відкладає роботу на стек, або знімає готову",
                  size=12, color=MUTED))

    # колонки: x-початок, ширина, заголовок
    cx_tok, w_tok = 50, 78
    cx_act, w_act = 138, 460
    cx_ops, w_ops = 608, 200
    cx_val, w_val = 818, 172
    rows = [
        ("2", "число — одразу на стек значень", "—", "2", None),
        ("*", "стек порожній → нíчого витісняти, відкладаємо", "*", "2", None),
        ("(", "бар'єр: усередині — своя зона пріоритету", "* (", "2", BARR),
        ("3", "число", "* (", "2 · 3", None),
        ("+", "зверху бар'єр ( → витісняти нíчого, відкладаємо", "* ( +", "2 · 3", None),
        ("4", "число", "* ( +", "2 · 3 · 4", None),
        (")", "згортаємо до бар'єра: 3 + 4 = 7, бар'єр знімаємо", "*", "2 · 7", BARR),
        ("−", "зверху * — сильніше → спрацьовує: 2 * 7 = 14", "−", "14", OPS),
        ("1", "число", "−", "14 · 1", None),
        ("⊣", "вхід скінчився → доганяємо все: 14 − 1 = 13", "—", "13", FIELD),
    ]

    y0, rh = 92, 42
    # шапка
    P.append(rect(cx_tok, y0, w_tok, 34, fill="#eef2f7", stroke="#c9d2dc", sw=1.4, rx=4))
    P.append(rect(cx_act, y0, w_act, 34, fill="#eef2f7", stroke="#c9d2dc", sw=1.4, rx=4))
    P.append(rect(cx_ops, y0, w_ops, 34, fill=OPSF, stroke=OPS, sw=1.4, rx=4))
    P.append(rect(cx_val, y0, w_val, 34, fill=VALSF, stroke=VALS, sw=1.4, rx=4))
    P.append(text(cx_tok + w_tok / 2, y0 + 22, "лексема", size=12, color=INK, bold=True))
    P.append(text(cx_act + w_act / 2, y0 + 22, "що робить машина", size=12, color=INK, bold=True))
    P.append(text(cx_ops + w_ops / 2, y0 + 22, "стек операторів", size=12, color=OPS, bold=True))
    P.append(text(cx_val + w_val / 2, y0 + 22, "стек значень", size=12, color=VALS, bold=True))

    for i, (tok, act, ops, vals, hl) in enumerate(rows):
        y = y0 + 40 + i * rh
        if hl:
            P.append(rect(cx_tok, y, cx_val + w_val - cx_tok, rh - 6,
                          fill="#fbfcfe", stroke=hl, sw=1.6, rx=5))
        P.append(text(cx_tok + w_tok / 2, y + 25, tok, size=16, color=INK, bold=True))
        P.append(text(cx_act + 14, y + 25, act, size=12.5, color=INK, anchor="start"))
        P.append(text(cx_ops + w_ops / 2, y + 25, ops, size=14, color=OPS, bold=True))
        P.append(text(cx_val + w_val / 2, y + 25, vals, size=14, color=VALS, bold=True))
        if i < len(rows) - 1 and not hl:
            P.append(line(cx_tok, y + rh - 3, cx_val + w_val, y + rh - 3, color="#eceff3", sw=1))

    P.append(text(W / 2, 540, "Робота лягає на стек рівно тоді, коли її ще не можна зробити, "
                              "і сходить рівно тоді, коли вже можна.", size=12.5, color=INK))
    render("img/expr-trace.svg", W, H, *P)


# ── Фігура 6: явний стек ↔ стек викликів — одна машина, дві подоби ────────────
# Той самий момент розбору 2*(3+(4-1)): ліворуч вкладеність тримає стек, який
# ми написали; праворуч — стек кадрів, який дала мова. Глибина та сама.
def fig_descent_vs_shunting():
    W, H = 1060, 580
    P = []
    P.append(text(W / 2, 38, "Одна машина, дві подоби: явний стек і стек викликів", size=17, color=INK, bold=True))
    P.append(text(W / 2, 62, "той самий момент розбору  2 * ( 3 + ( 4 − 1 ) )  —  щойно прочитано 1",
                  size=12, color=MUTED))

    base_y = 470

    # ── ліворуч: сортувальна станція, явний стек операторів ──
    lx = 260
    P.append(rect(40, 88, 440, 452, fill="#fcfdfe", stroke="#dfe4ea", sw=1.5, rx=10))
    P.append(text(lx, 120, "Сортувальна станція", size=14.5, color=INK, bold=True))
    P.append(text(lx, 142, "стек операторів — наш власний масив", size=11.5, color=MUTED))
    cells = [("*", OPSF, OPS), ("(", BARRF, BARR), ("+", OPSF, OPS), ("(", BARRF, BARR), ("−", OPSF, OPS)]
    P.append(_col(lx, base_y, cells, cw=72, ch=40, size=17))
    P.append(line(lx - 60, base_y, lx + 60, base_y, color="#cfd4da", sw=1.6))
    P.append(text(lx, base_y + 22, "глибина 5 — вкладеність видно очима", size=11.5, color=OPS, bold=True))
    P.append(text(lx, base_y - 5 * 40 - 14, "вершина", size=11, color=MUTED))

    # ── праворуч: рекурсивний спуск, стек кадрів ──
    rx_ = 800
    P.append(rect(580, 88, 440, 452, fill="#fcfdfe", stroke="#dfe4ea", sw=1.5, rx=10))
    P.append(text(rx_, 120, "Рекурсивний спуск", size=14.5, color=INK, bold=True))
    P.append(text(rx_, 142, "стек кадрів — його веде сама мова", size=11.5, color=MUTED))
    frames = [
        ("expr «2*(3+(4−1))»", VALSF, VALS),
        ("factor бачить (", BARRF, BARR),
        ("expr «3+(4−1)»", VALSF, VALS),
        ("factor бачить (", BARRF, BARR),
        ("expr «4−1»", VALSF, VALS),
    ]
    P.append(_col(rx_, base_y, frames, cw=290, ch=40, size=13))
    P.append(line(rx_ - 160, base_y, rx_ + 160, base_y, color="#cfd4da", sw=1.6))
    P.append(text(rx_, base_y + 22, "глибина 5 — та сама, лише не наша", size=11.5, color=VALS, bold=True))
    P.append(text(rx_, base_y - 5 * 40 - 14, "поточний виклик", size=11, color=MUTED))

    P.append(text(rx_, base_y + 42, "(кадри term/factor між рівнями опущено)", size=10.5, color=MUTED))

    # звʼязок
    P.append(arrow(lx + 100, 300, rx_ - 170, 300, color=INK, sw=1.6))
    P.append(text((lx + rx_) / 2 - 30, 288, "та сама LIFO-дисципліна", size=11.5, color=INK, bold=True))

    P.append(text(W / 2, 562, "Вкладеність не зникає, коли стек прибрати з коду, — вона просто переїжджає "
                              "в стек викликів.", size=12.5, color=INK))
    render("img/descent-vs-shunting.svg", W, H, *P)


# ═══ Фігури до вставки hist-pushdown-store.md ════════════════════════════════

ENG   = "#8a6d1f"   # інженерна нитка (тепле — залізо, компілятори)
ENGF  = "#fdf4dd"
LNG   = "#2457d6"   # мовознавча нитка (холодне — теорія, граматики)
LNGF  = "#e9eefb"
JOIN  = "#27ae60"   # місце, де нитки зійшлися
JOINF = "#e8f6ed"


# ── Фігура 7: дві нитки, що йшли нарізно й зійшлися в 1962–63 ─────────────────
# Головна думка вставки: стек і клас мов винайшли ОКРЕМО, з різних потреб;
# теорема 1962–63 лише виявила, що це той самий предмет.
def fig_two_threads():
    W, H = 1040, 700
    P = []
    P.append(text(W / 2, 40, "Дві нитки, що не знали одна про одну", size=18, color=INK, bold=True))
    P.append(text(W / 2, 64, "стек винайшли інженери для формул; клас мов описали мовознавці для речень",
                  size=12.5, color=MUTED))

    lx, rx_ = 260, 780          # центри колонок
    cw = 420                    # ширина картки
    ys = [150, 232, 314, 396]   # рядки подій

    # заголовки колонок
    P.append(fitbox(lx - cw / 2, 96, cw, 40, "ІНЖЕНЕРИ: як порахувати формулу",
                    size=14, fill=ENGF, stroke=ENG, sw=2, bold=True, color=ENG))
    P.append(fitbox(rx_ - cw / 2, 96, cw, 40, "МОВОЗНАВЦІ: як розібрати речення",
                    size=14, fill=LNGF, stroke=LNG, sw=2, bold=True, color=LNG))

    left = [
        ("1955  ·  Мюнхен", "Бауер і Замельзон кладуть відкладені\nдії «навпаки» — принцип «Keller» (льох)"),
        ("1957  ·  патент", "заявка від 30 березня; стек як\nмеханізм обчислення формул"),
        ("1960  ·  ALGOL 60", "Дейкстра вживає слово «стек» —\nі воно витісняє «pushdown store»"),
        ("Але", "нікому не спадає питання:\nЯКИЙ КЛАС МОВ бере машина зі стеком?"),
    ]
    right = [
        ("1956  ·  Хомський", "скінченні стани не описують мови;\nпотрібні сильніші граматики"),
        ("1959  ·  Хомський", "чотири типи граматик; для типу 2\nМАШИНИ НЕМАЄ — сама лише граматика"),
        ("1960/61  ·  Оттінґер", "розбираючи російську, кладе\nВІДКЛАДЕНІ ПЕРЕДБАЧЕННЯ на «pushdown store»"),
        ("Але", "це метод розбору, а не теорема:\nщо саме бере ця машина — не сказано"),
    ]

    for i, (hd, body) in enumerate(left):
        y = ys[i]
        acc = ENG if i < 3 else MUTED
        P.append(rect(lx - cw / 2, y, cw, 66, fill=BG, stroke=acc, sw=1.6))
        P.append(text(lx - cw / 2 + 14, y + 21, hd, size=12.5, color=acc, anchor="start", bold=True))
        P.append(mtext(lx - cw / 2 + 14, y + 40, body, size=11.5, color=INK, anchor="start", lh=1.35))

    for i, (hd, body) in enumerate(right):
        y = ys[i]
        acc = LNG if i < 3 else MUTED
        P.append(rect(rx_ - cw / 2, y, cw, 66, fill=BG, stroke=acc, sw=1.6))
        P.append(text(rx_ - cw / 2 + 14, y + 21, hd, size=12.5, color=acc, anchor="start", bold=True))
        P.append(mtext(rx_ - cw / 2 + 14, y + 40, body, size=11.5, color=INK, anchor="start", lh=1.35))

    # нитки вниз, до місця зустрічі
    P.append(arrow(lx, ys[3] + 70, lx + 130, 508, color=ENG, sw=2))
    P.append(arrow(rx_, ys[3] + 70, rx_ - 130, 508, color=LNG, sw=2))

    # місце зустрічі
    jw = 700
    P.append(rect(W / 2 - jw / 2, 514, jw, 76, fill=JOINF, stroke=JOIN, sw=2.4))
    P.append(text(W / 2, 540, "1962  ·  Хомський:  граматика типу 2  ⇄  магазинна пам'ять",
                  size=15, color=JOIN, bold=True))
    P.append(text(W / 2, 566, "1963 — те саме незалежно доводить Іві; того ж року Шютценберже бере "
                              "детерміновану гілку",
                  size=12, color=INK))
    P.append(text(W / 2, 583, "нічого нового не збудовано — виявлено, що дві нитки тримали ОДИН предмет",
                  size=11.5, color=MUTED))

    # кода
    P.append(rect(W / 2 - jw / 2, 606, jw, 44, fill="#fdecea", stroke=POS, sw=1.8))
    P.append(text(W / 2, 626, "1966  ·  ALPAC: фінансування машинного перекладу згорнуто",
                  size=13, color=POS, bold=True))
    P.append(text(W / 2, 643, "питання вмирає — машина, знайдена по дорозі, лишається назавжди",
                  size=11.5, color=INK))

    P.append(text(W / 2, 676, "Стек був старий і чужий теорії; клас мов був описаний і безмашинний. "
                              "Відкриттям стала не деталь, а рівність.",
                  size=12.5, color=INK))
    render("img/two-threads.svg", W, H, *P)


# ── Фігура 8: що саме Оттінґер клав на стек — ВІДКЛАДЕНІ ПЕРЕДБАЧЕННЯ ─────────
# Ключ до походження: магазин тримав не символи входу, а НЕВИКОНАНІ ОБІЦЯНКИ
# розбору. Вкладене речення змушує відкласти чинне передбачення й вернутись
# до нього ПІЗНІШЕ — і саме «останнім відклав — першим вернувся» дає LIFO.
def fig_prediction_stack():
    W, H = 1080, 500
    P = []
    P.append(text(W / 2, 40, "Що Оттінґер клав на «pushdown store»: невиконані передбачення",
                  size=18, color=INK, bold=True))
    P.append(text(W / 2, 64, "«Кіт, якого пес налякав, утік.» — підрядне речення розриває головне навпіл",
                  size=13, color=MUTED))

    xs = [130, 335, 540, 745, 950]
    base_y = 390
    cw, ch = 174, 34

    words = ["Кіт", "якого", "пес", "налякав", "утік"]
    acts = ["відкладаю передбачення:\nдалі мусить бути присудок",
            "підрядне почалося —\nвідкладаю ЩЕ одне",
            "іменник підрядного;\nнічого не змінює",
            "присудок підрядного є —\nобіцянку виконано",
            "присудок головного є —\nобіцянку виконано"]
    marks = ["push", "push", "—", "pop", "pop"]

    HEAD = ("присудок головного", LNGF, LNG)
    SUB = ("присудок підрядного", ENGF, ENG)
    snaps = [[HEAD], [HEAD, SUB], [HEAD, SUB], [HEAD], []]

    P.append(line(70, base_y, 1010, base_y, color="#cfd4da", sw=1.6))

    for i, x in enumerate(xs):
        # слово входу
        P.append(fitbox(x - cw / 2, 96, cw, 34, words[i], size=15,
                        fill="#f4f6f8", stroke=INK, sw=1.8, bold=True))
        # позначка дії
        mc = {"push": LNG, "pop": JOIN, "—": MUTED}[marks[i]]
        P.append(text(x, 152, marks[i], size=13, color=mc, bold=True))
        # стовпчик стека
        for j, (lab, fill, stroke) in enumerate(snaps[i]):
            y = base_y - (j + 1) * ch
            P.append(fitbox(x - cw / 2, y, cw, ch, lab, size=12,
                            fill=fill, stroke=stroke, sw=1.6, rx=3, bold=True))
        if not snaps[i]:
            P.append(text(x, base_y - 18, "порожньо", size=12, color=JOIN, bold=True))
        # пояснення під підлогою
        P.append(mtext(x, base_y + 22, acts[i], size=11, color=INK, lh=1.3))

    P.append(text(W / 2, 466, "Друге передбачення відклали останнім — і вернулися до нього першим. "
                              "Ця нерівність у часі, а не якийсь вибір інженера, і є LIFO.",
                  size=12.5, color=INK))
    render("img/prediction-stack.svg", W, H, *P)


# ══ Фігури до вставки math-pda-cfg-equivalence.md ════════════════════════
EQ_DONE  = "#e9ecef"   # прочитаний вхід (минуле)
EQ_DONES = "#adb5bd"
EQ_HEAD  = "#c0392b"   # головка входу
EQ_PANEL = "#f7f9fc"
EQ_PANB  = "#c8d2e0"


def _eq_brace(xa, xb, y, lab, col=INK, size=12, bold=True):
    """Горизонтальна дужка [xa..xb] на висоті y з підписом під нею."""
    return "".join([
        line(xa, y, xb, y, color=col, sw=1.6),
        line(xa, y - 5, xa, y + 5, color=col, sw=1.6),
        line(xb, y - 5, xb, y + 5, color=col, sw=1.6),
        text((xa + xb) / 2, y + 17, lab, size=size, color=col, bold=bold),
    ])


# ── Фігура: стек тримає недороблену частину виводу ────────────────
# Головна думка вставки: прочитане · стек = сентенційна форма лівого виводу.
# Кожен рядок — знімок прогону; сірі клітини (минуле) і сині (борг на стеку)
# разом читаються як поточна сентенційна форма, головка стоїть на розрізі.
def fig_cfg_pda_derivation():
    W, H = 960, 530
    P = []
    P.append(text(W / 2, 34, "Стек тримає недороблену частину виводу", size=17, color=INK, bold=True))
    P.append(text(W / 2, 57, "низхідний автомат на вході «()()» за граматикою  S → ( S ) S | ε",
                  size=12, color=MUTED))

    ly = 88
    P.append(rect(92, ly - 10, 20, 20, fill=EQ_DONE, stroke=EQ_DONES, sw=1.4, rx=3))
    P.append(text(118, ly + 5, "прочитаний вхід", size=11, color=MUTED, anchor="start"))
    P.append(rect(240, ly - 10, 20, 20, fill=MARKF, stroke=MARK, sw=1.4, rx=3))
    P.append(text(266, ly + 5, "стек (вершина ліворуч)", size=11, color=MUTED, anchor="start"))
    P.append(line(430, ly - 12, 430, ly + 12, color=EQ_HEAD, sw=2.4))
    P.append(text(440, ly + 5, "головка входу", size=11, color=MUTED, anchor="start"))

    P.append(text(52, 120, "крок", size=11, color=MUTED, bold=True))
    P.append(text(92, 120, "рядок = сентенційна форма", size=11, color=MUTED, anchor="start", bold=True))
    P.append(text(360, 120, "дія", size=11, color=MUTED, anchor="start", bold=True))

    rows = [
        ("0", "",     "S",    "старт: увесь борг — на стеку", False),
        ("1", "",     "(S)S", "розгортання  S → ( S ) S        ← здогад", True),
        ("2", "(",    "S)S",  "звірка «(» — pop", False),
        ("3", "(",    ")S",   "розгортання  S → ε              ← здогад", True),
        ("4", "()",   "S",    "звірка «)» — pop", False),
        ("5", "()",   "(S)S", "розгортання  S → ( S ) S        ← здогад", True),
        ("6", "()(",  "S)S",  "звірка «(» — pop", False),
        ("7", "()(",  ")S",   "розгортання  S → ε              ← здогад", True),
        ("8", "()()", "S",    "звірка «)» — pop", False),
        ("9", "()()", "",     "розгортання  S → ε   →   стек порожній: ПРИЙОМ", True),
    ]
    x0, cw = 92, 32
    for i, (n, done, stk, act, is_exp) in enumerate(rows):
        y = 146 + i * 34
        P.append(text(52, y + 5, n, size=12, color=MUTED))
        x = x0
        for ch in done:
            P.append(rect(x, y - 13, cw, 26, fill=EQ_DONE, stroke=EQ_DONES, sw=1.3, rx=3))
            P.append(text(x + cw / 2, y + 5, ch, size=14, color=MUTED, bold=True))
            x += cw
        xh = x
        for ch in stk:
            P.append(rect(x, y - 13, cw, 26, fill=MARKF, stroke=MARK, sw=1.4, rx=3))
            P.append(text(x + cw / 2, y + 5, ch, size=14, color=INK, bold=True))
            x += cw
        P.append(line(xh, y - 17, xh, y + 17, color=EQ_HEAD, sw=2.4))
        P.append(text(360, y + 5, act, size=12, color=(MARK if is_exp else MUTED),
                      anchor="start", bold=is_exp))

    P.append(text(W / 2, 496, "Кожен рядок, прочитаний зліва направо, — поточна сентенційна форма лівого виводу.",
                  size=12, color=INK))
    P.append(text(W / 2, 516, "Сині кроки міняють форму — це і є кроки виводу; сірі лише посувають головку. "
                              "Сині підряд: S→(S)S, S→ε, S→(S)S, S→ε, S→ε.",
                  size=11, color=MUTED))
    render("img/cfg-pda-derivation.svg", W, H, *P)


# ── Фігура: епізод стека = змінна-трійка [q X p] ──────────────────
# Висота стека в часі. Поки X лежить, шар під ним заморожений — тому епізод
# самодостатній і залежить лише від (q, X, p). Усередині — вкладені епізоди
# Y₁ і Y₂ зі зчепленими станами: вихід одного = вхід наступного.
def fig_cfg_pda_episode():
    W, H = 920, 552
    P = []
    P.append(text(W / 2, 34, "Змінна-трійка [q X p]: епізод життя одного символа на стеку",
                  size=17, color=INK, bold=True))
    P.append(text(W / 2, 57, "поки X лежить на стеку, все під ним недоторканне — тому епізод самодостатній",
                  size=12, color=MUTED))

    x0, x1 = 100, 800
    dt = (x1 - x0) / 14.0
    ybase, unit = 380, 46
    X_ = lambda t: x0 + dt * t
    Y_ = lambda h: ybase - unit * h

    P.append(text(x0, 112, "висота стека ↑", size=11, color=MUTED, anchor="start"))
    P.append(text(x1, 112, "час, прочитаний вхід →", size=11, color=MUTED, anchor="end"))

    P.append(line(x0, 140, x0, ybase, color="#cfd4da", sw=1.4))
    P.append(line(x0, ybase, x1 + 12, ybase, color="#cfd4da", sw=1.4))
    for h in range(0, 6):
        P.append(line(x0 - 5, Y_(h), x0, Y_(h), color="#cfd4da", sw=1.2))
        P.append(text(x0 - 10, Y_(h) + 4, str(h), size=10, color=MUTED, anchor="end"))

    hs = [1, 2, 3, 4, 5, 4, 3, 2, 3, 4, 3, 2, 1, 1]

    P.append(rect(X_(1), Y_(1), X_(12) - X_(1), unit, fill="#f0f1f3", stroke="#dcdfe3", sw=1.2, rx=0))
    P.append(text((X_(1) + X_(12)) / 2, Y_(1) + 29,
                  "цей шар заморожений: під X автомат не заглядає", size=11, color=MUTED))
    P.append(line(X_(1), Y_(1), X_(12), Y_(1), color=MARK, sw=1.6, dash="6 4"))

    for t in range(len(hs)):
        P.append(line(X_(t), Y_(hs[t]), X_(t + 1), Y_(hs[t]), color=INK, sw=2.4))
        if t + 1 < len(hs) and hs[t + 1] != hs[t]:
            P.append(line(X_(t + 1), Y_(hs[t]), X_(t + 1), Y_(hs[t + 1]), color=INK, sw=2.4))

    P.append(text(X_(1), Y_(2) - 24, "X на вершині", size=11, color=MARK, bold=True))
    P.append(text(X_(12) + 14, Y_(1) - 16, "рівень повернувся під X",
                  size=11, color=MARK, anchor="start", bold=True))

    for cx, cy, lab in [(X_(1), Y_(2), "q"), (X_(2), Y_(3), "r"),
                        (X_(7), Y_(2), "s₁"), (X_(12), Y_(1), "p")]:
        P.append(circle(cx, cy, 13, fill=BG, stroke=MARK, sw=2))
        P.append(text(cx, cy + 4, lab, size=11, color=MARK, bold=True))

    P.append(_eq_brace(X_(1), X_(12), 402, "[q X p]  —  усе слово, прочитане за епізод", col=MARK))
    P.append(_eq_brace(X_(1), X_(2), 448, "a", col=MUTED, size=11))
    P.append(_eq_brace(X_(2), X_(7), 448, "[r Y₁ s₁]", col=GREEN, size=11))
    P.append(_eq_brace(X_(7), X_(12), 448, "[s₁ Y₂ p]", col=GREEN, size=11))

    bx, by, bw, bh = 90, 480, 740, 58
    P.append(rect(bx, by, bw, bh, fill="#f6f8fb", stroke="#d6dde8", sw=1.5, rx=8))
    P.append(text(bx + 16, by + 24, "перехід  δ(q, a, X) ∋ (r, Y₁Y₂)      дає правило      "
                                    "[q X p] → a [r Y₁ s₁] [s₁ Y₂ p]",
                  size=13, color=INK, anchor="start", bold=True))
    P.append(text(bx + 16, by + 45, "кінці зчеплені доміно: s₁ — вихід епізоду Y₁ і водночас вхід епізоду Y₂",
                  size=11, color=MUTED, anchor="start"))
    render("img/cfg-pda-episode.svg", W, H, *P)


# ── Фігура: двійник теореми Кліні ─────────────────────────────
# Дві сходинки, та сама будова доведення: легкий бік — синтаксично керована
# побудова машини за формулою; важкий — пара станів у імені шматка. Різниця
# лише в третьому індексі: у Кліні він має стелю, тут — ні.
def fig_cfg_pda_kleene_twin():
    W, H = 980, 500
    P = []
    P.append(text(W / 2, 34, "Двійник теореми Кліні — і в чому рівно один поверх різниці",
                  size=17, color=INK, bold=True))

    def rung(y0, tint, edge, name, fml, mach, easy, hard, thm, eqn, mem, accent):
        Q = [rect(40, y0, 900, 190, fill=tint, stroke=edge, sw=1.8, rx=10)]
        Q.append(text(58, y0 + 24, name, size=12, color=MUTED, anchor="start", bold=True))
        b, _w, _h = textbox(200, y0 + 80, fml, size=13, fill=BG, stroke=edge, sw=1.6, min_w=160)
        Q.append(b)
        b, _w, _h = textbox(790, y0 + 80, mach, size=13, fill=BG, stroke=edge, sw=1.6, min_w=160)
        Q.append(b)
        Q.append(arrow(295, y0 + 62, 690, y0 + 62, color=MUTED, sw=1.8))
        Q.append(text(492, y0 + 52, easy, size=11, color=MUTED))
        Q.append(arrow(690, y0 + 100, 295, y0 + 100, color=accent, sw=1.8))
        Q.append(text(492, y0 + 118, hard, size=11, color=accent, bold=True))
        Q.append(text(492, y0 + 82, thm, size=12, color=INK, bold=True))
        Q.append(text(58, y0 + 155, eqn, size=12, color=INK, anchor="start"))
        Q.append(text(58, y0 + 176, mem, size=11, color=MUTED, anchor="start"))
        return "".join(Q)

    P.append(rung(60, EQ_PANEL, EQ_PANB, "ЩАБЕЛЬ 1 · РЕГУЛЯРНІ",
                  ["Регулярний вираз", "(a|b)*ab"], ["Скінченний", "автомат"],
                  "гаджет на кожен оператор, склейка через ε",
                  "Rᵏ(i, j):  пара станів  +  СТЕЛЯ k",
                  "теорема Кліні",
                  "рівняння лінійні:  X = A·X ∪ B  ⟹  X = A*·B  (Арден) — розв'язок є, і це і є зірка",
                  "стек зайвий: на ньому завжди рівно одна змінна, а одна комірка це і є стан",
                  MARK))
    P.append(rung(268, "#f3fbf6", GREEN, "ЩАБЕЛЬ 2 · КОНТЕКСТНО-ВІЛЬНІ",
                  ["КВ-граматика", "S → ( S ) S | ε"], ["Магазинний", "автомат"],
                  "правило = розгортання, термінал = звірка",
                  "[q X p]:  пара станів  +  символ стека X",
                  "наша теорема",
                  "рівняння квадратні:  S = ( S ) S ∪ ε  ⟹  розв'язку в {∪, ·, *} нема — граматика й є відповідь",
                  "стек без стелі: рекурсія епізодів не спадає до бази за скінченне число щаблів",
                  GREEN))

    P.append(text(W / 2, 482, "Будова доведення та сама — аж до квадратичного роздуву по станах. "
                              "Різниця одна: там третій індекс має стелю, тут — ні.",
                  size=12, color=INK))
    render("img/cfg-pda-kleene-twin.svg", W, H, *P)


if __name__ == "__main__":
    fig_stack_run()
    fig_machine_model()
    fig_hierarchy()
    fig_precedence_defer()
    fig_expr_trace()
    fig_descent_vs_shunting()
    fig_two_threads()
    fig_prediction_stack()
    fig_cfg_pda_derivation()
    fig_cfg_pda_episode()
    fig_cfg_pda_kleene_twin()
    print("OK: cfg-pda-derivation.svg, cfg-pda-episode.svg, cfg-pda-kleene-twin.svg, "
          "stack-run.svg, machine-model.svg, hierarchy.svg, "
          "precedence-defer.svg, expr-trace.svg, descent-vs-shunting.svg, "
          "two-threads.svg, prediction-stack.svg")
