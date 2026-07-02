# -*- coding: utf-8 -*-
"""Фігури до теми «Позичання часу в латч-конвеєрах».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Жорстка стіна тригера ↔ прозоре вікно засувки ────────────────────────
def fig_wall_vs_window():
    W, H = 720, 340
    els = []
    # --- ліворуч: тригер (жорсткий дедлайн) ---
    lx = 40
    els.append(text(lx + 150, 54, "Тригер: жорстка стіна", size=15, bold=True, anchor="middle"))
    # вісь часу
    y0 = 110
    els.append(line(lx, y0, lx + 300, y0, color=MUTED, sw=1.4))
    # фронт (вертикальна стіна)
    edge = lx + 230
    els.append(line(edge, 78, edge, 250, color=POS, sw=2.5))
    els.append(text(edge, 268, "фронт", size=12, color=POS, bold=True))
    # смуга логіки, що встигає (зелена)
    els.append(rect(lx + 10, y0 - 16, 210, 32, fill="#eafaf0", stroke=FIELD, sw=1.6))
    els.append(text(lx + 115, y0 + 5, "логіка встигла", size=12, color=FIELD))
    # смуга логіки, що НЕ встигла (червона, б'ється об стіну)
    els.append(rect(lx + 10, y0 + 42, 245, 32, fill="#fdecea", stroke=POS, sw=1.6))
    els.append(text(lx + 120, y0 + 63, "не встигла → збій", size=12, color=POS))
    els.append(text(lx + 150, 300, "устигни ДО фронту, інакше втрата", size=11, color=MUTED))

    # --- праворуч: засувка (прозоре вікно) ---
    rx = 400
    els.append(text(rx + 150, 54, "Засувка: прозоре вікно", size=15, bold=True, anchor="middle"))
    y1 = 110
    els.append(line(rx, y1, rx + 300, y1, color=MUTED, sw=1.4))
    # вікно прозорості (зелена смуга по осі)
    w0 = rx + 150
    w1 = rx + 260
    els.append(rect(w0, 78, w1 - w0, 172, fill="#eafaf0", stroke=FIELD, sw=1.6))
    els.append(text((w0 + w1) / 2, 96, "прозоро", size=11, color=FIELD, bold=True))
    els.append(text(w1, 268, "спад", size=12, color=NEG, bold=True))
    els.append(line(w1, 78, w1, 250, color=NEG, sw=2.5))
    # логіка, що зайшла у вікно (жовтогаряча, все одно спіймана)
    els.append(rect(rx + 10, y1 - 16, 190, 32, fill="#eafaf0", stroke=FIELD, sw=1.6))
    els.append(text(rx + 105, y1 + 5, "устигла", size=12, color=FIELD))
    els.append(rect(rx + 10, y1 + 42, 225, 32, fill="#fff6e6", stroke="#e0a500", sw=1.6))
    els.append(text(rx + 120, y1 + 63, "спізнилась — та спіймана", size=11, color="#a06f00"))
    els.append(text(rx + 150, 300, "лови БУДЬ-КОЛИ у вікні — аж до спаду", size=11, color=MUTED))

    render(os.path.join(IMG, "wall-vs-window.svg"), W, H, *els)


# ── 2. Позичання часу через межу двох ступенів ───────────────────────────────
def fig_borrow_across():
    W, H = 720, 300
    els = []
    x0, x1 = 60, 660
    # шкала часу
    scale = (x1 - x0) / 100.0   # 100 умовних одиниць = такт
    def X(t): return x0 + t * scale

    # межі тактів: два послідовні такти A|B, межа-засувка посередині
    tickY = 250
    els.append(line(x0, tickY, x1, tickY, color=MUTED, sw=1.4))
    for t, lab in [(0, "старт A"), (50, "номінальна\nмежа"), (100, "кінець B")]:
        els.append(line(X(t), tickY - 6, X(t), tickY + 6, color=MUTED, sw=1.4))
    els.append(text(X(0), tickY + 22, "старт A", size=11, color=MUTED))
    els.append(text(X(100), tickY + 22, "кінець B", size=11, color=MUTED))

    # прозоре вікно засувки-межі (навколо t=50)
    wa, wb = 44, 62
    els.append(rect(X(wa), 70, X(wb) - X(wa), 150, fill="#eafaf0", stroke=FIELD, sw=1.4))
    els.append(text(X((wa + wb) / 2), 60, "вікно прозорості межі", size=11, color=FIELD, bold=True))
    els.append(line(X(50), 70, X(50), tickY, color=MUTED, sw=1.2, dash="4 4"))
    els.append(text(X(50), 244, "номінал", size=10, color=MUTED))

    # ступінь A — довгий, залазить у вікно (позичає)
    ay = 110
    els.append(rect(X(0), ay - 16, X(58) - X(0), 32, fill="#fdecea", stroke=POS, sw=1.7))
    els.append(text(X(29), ay + 5, "ступінь A — повільний (58)", size=12, color=POS))
    els.append(text(X(54), ay - 26, "залазить на 8 у вікно", size=10, color=POS))

    # ступінь B — короткий, стартує пізно, все одно встигає
    by = 170
    els.append(rect(X(58), by - 16, X(100) - X(58), 32, fill="#eafaf0", stroke=FIELD, sw=1.7))
    els.append(text(X(79), by + 5, "ступінь B — швидкий (42)", size=12, color=FIELD))
    els.append(text(X(58), by - 26, "стартує пізно, та вкладається", size=10, color=FIELD))

    # підсумкова дужка: разом 100
    els.append(line(X(0), 40, X(100), 40, color=INK, sw=1.4))
    els.append(text(X(50), 32, "разом = 2 такти (A+B = 58+42 = 100) — межа зсунулась, сума ні", size=11, bold=True))

    render(os.path.join(IMG, "borrow-across.svg"), W, H, *els)


# ── 3. Двофазний такт: де живе вікно позики ─────────────────────────────────
def fig_two_phase():
    W, H = 700, 320
    els = []
    x0, x1 = 70, 660
    T = x1 - x0
    per = T / 2.0          # два повні періоди у вікні
    hi = 26               # висота меандру

    def clockrow(y, label, shift, color):
        els.append(text(x0 - 8, y - hi / 2, label, size=13, color=color, bold=True, anchor="end"))
        # два періоди; кожен: половина висока, половина низька
        lvl = y  # низький рівень
        pts = []
        # будуємо простий меандр: 4 півперіоди
        seg = per / 2.0
        x = x0 + shift
        # почати з базового відрізка до shift
        prevx = x0
        prevy = lvl
        states = [0, 1, 0, 1, 0]  # рівні на межах півперіодів (0 низ,1 верх)
        # намалюємо руками: періоди зі зсувом фаз через прямокутники «високо»
        highs = []
        # φ: високий у [shift, shift+seg], [shift+per, shift+per+seg]
        for k in range(2):
            hx0 = x0 + shift + k * per
            hx1 = hx0 + seg
            if hx1 > x1: hx1 = x1
            if hx0 < x1:
                highs.append((max(hx0, x0), min(hx1, x1)))
        # лінія: базовий низ уздовж усього
        els.append(line(x0, lvl, x1, lvl, color=color, sw=1.2, dash="2 3"))
        for (hx0, hx1) in highs:
            els.append(rect(hx0, y - hi, hx1 - hx0, hi, fill="none", stroke=color, sw=2.0, rx=2))
        return highs

    yf1 = 90
    yf2 = 170
    h1 = clockrow(yf1, "φ1", 0, NEG)
    h2 = clockrow(yf2, "φ2", per / 2.0, POS)

    # зазор «неперекриття» між фазами
    if h1 and h2:
        gapx = h1[0][1]
        els.append(line(gapx, 60, gapx, 250, color=MUTED, sw=1.0, dash="3 3"))
        els.append(text(gapx + 6, 52, "неперекриття (обидві 0)", size=10, color=MUTED, anchor="start"))

    # пояснювальний рядок: логіка між латчами φ1 і φ2
    ly = 240
    els.append(rect(x0, ly, per, 34, fill=FILL, stroke=LINE, sw=1.4))
    els.append(fitbox(x0, ly, per, 34, "логіка A (латч φ1 → латч φ2)", size=11))
    els.append(rect(x0 + per, ly, T - per, 34, fill=FILL, stroke=LINE, sw=1.4))
    els.append(fitbox(x0 + per, ly, T - per, 34, "логіка B (латч φ2 → латч φ1)", size=11))
    els.append(text((x0 + x1) / 2, 300, "дві протифазні хвилі; латчі відчинені по черзі — позика живе у півперіоді прозорості",
                    size=11, color=MUTED))

    render(os.path.join(IMG, "two-phase.svg"), W, H, *els)


# ── 4. Бюджет: скільки можна позичити ────────────────────────────────────────
def fig_budget():
    W, H = 680, 260
    els = []
    x0 = 60
    bar_w = 560
    y = 90
    barh = 40
    # повний бар = такт T
    els.append(text(x0, 56, "Бюджет часу однієї межі-засувки", size=14, bold=True, anchor="start"))
    els.append(rect(x0, y, bar_w, barh, fill="#f0f2f5", stroke=LINE, sw=1.5))
    # половина — «нормальний» такт, друга половина — доступна для позики (до T/2)
    half = bar_w / 2.0
    els.append(rect(x0, y, half, barh, fill="#eaf0fd", stroke=NEG, sw=1.5))
    els.append(text(x0 + half / 2, y + barh / 2 + 5, "робота ступеня (номінал)", size=12, color=NEG))
    els.append(rect(x0 + half, y, half, barh, fill="#eafaf0", stroke=FIELD, sw=1.5))
    els.append(text(x0 + half + half / 2, y + barh / 2 + 5, "стеля позики ≈ T/2", size=12, color=FIELD))

    # позначки під баром
    els.append(line(x0, y + barh + 8, x0, y + barh + 16, color=MUTED, sw=1.2))
    els.append(line(x0 + half, y + barh + 8, x0 + half, y + barh + 16, color=MUTED, sw=1.2))
    els.append(line(x0 + bar_w, y + barh + 8, x0 + bar_w, y + barh + 16, color=MUTED, sw=1.2))
    els.append(text(x0, y + barh + 30, "0", size=11, color=MUTED))
    els.append(text(x0 + half, y + barh + 30, "фаза (T/2)", size=11, color=MUTED))
    els.append(text(x0 + bar_w, y + barh + 30, "такт T", size=11, color=MUTED, anchor="end"))

    els.append(text(x0, 210, "Позичати можна лише стільки, скільки триває прозорість (пів такту).",
                    size=12, color=INK, anchor="start"))
    els.append(text(x0, 230, "Що позичив ступінь — те відняв у наступного: сумарний бюджет не росте.",
                    size=12, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "budget.svg"), W, H, *els)


# ── 5. Виведення бюджету: вікно, дедлайн W−t_setup, перетікання borrow ───────
def fig_borrow_budget():
    """Часова вісь одного такту для math-вставки: вікно прозорості 0..W,
    дедлайн захоплення на W−t_setup, виступ ступеня A за номінал W (borrow_out)
    = пізній старт ступеня B (borrow_in). Показує, що позика перетікає."""
    W, H = 720, 340
    els = []
    x0, xT = 70, 650
    scale = (xT - x0) / 10.0        # 10 нс = такт T
    def X(t): return x0 + t * scale

    Wns = 5.0                        # W = T/2 = 5 нс
    setup = 0.4                      # t_setup (умовно, для видимості на осі)
    dl = Wns - setup                 # дедлайн захоплення
    logicA = 6.5                     # t_logic(A)
    # borrow_out(A) = logicA - W (ідеалізовано t_cq≈0)
    bo = logicA - Wns                # 1.5

    # --- вісь часу з мітками 0, W=T/2, T ---
    axY = 300
    els.append(line(x0, axY, xT, axY, color=MUTED, sw=1.4))
    for t, lab in [(0.0, "0"), (Wns, "W = T/2"), (10.0, "T")]:
        els.append(line(X(t), axY - 6, X(t), axY + 6, color=MUTED, sw=1.4))
        an = "start" if t == 0.0 else ("end" if t == 10.0 else "middle")
        els.append(text(X(t), axY + 22, lab, size=12, color=MUTED, anchor=an))

    # --- вікно прозорості 0..W (світло-зелена підкладка) ---
    els.append(rect(X(0), 70, X(Wns) - X(0), axY - 70, fill="#f0fbf4", stroke="none"))
    els.append(text(X(Wns / 2), 62, "вікно прозорості латча (0 … W)", size=12, color=FIELD, bold=True))
    # спад латча на W + лінія
    els.append(line(X(Wns), 70, X(Wns), axY, color=NEG, sw=2.2))
    els.append(text(X(Wns) + 4, axY - 10, "спад", size=11, color=NEG, anchor="start"))
    # дедлайн захоплення W − t_setup
    els.append(line(X(dl), 84, X(dl), axY, color=POS, sw=1.6, dash="4 3"))
    els.append(text(X(dl), 80, "дедлайн W − t_setup", size=11, color=POS, anchor="middle"))

    # --- ступінь A: смуга 0..logicA, залазить за W ---
    ayc = 130
    els.append(rect(X(0), ayc - 15, X(logicA) - X(0), 30, fill="#fdecea", stroke=POS, sw=1.7))
    els.append(text(X(logicA / 2), ayc + 4, "ступінь A — логіка (t_logic = 6.5)", size=12, color=POS))
    # виступ за номінал W = borrow_out(A) (штрихування яскравіше)
    els.append(rect(X(Wns), ayc - 15, X(logicA) - X(Wns), 30, fill="#f7b7ad", stroke=POS, sw=1.7))
    els.append(text(X((Wns + logicA) / 2), ayc - 24, "borrow_out(A) = 1.5", size=10, color=POS, bold=True))

    # --- ступінь B: стартує в момент захоплення A (= W + bo), треба 3 ---
    byc = 200
    bStart = Wns + bo                # 6.5 — пізній старт B
    logicB = 3.0
    bEnd = bStart + logicB           # 9.5
    els.append(rect(X(bStart), byc - 15, X(bEnd) - X(bStart), 30, fill="#eafaf0", stroke=FIELD, sw=1.7))
    els.append(text(X((bStart + bEnd) / 2), byc + 4, "ступінь B — логіка (t_logic = 3)", size=12, color=FIELD))
    # пізній старт = borrow_in(B): показати відрізок від W до bStart
    els.append(rect(X(Wns), byc - 15, X(bStart) - X(Wns), 30, fill="#d6f0e0", stroke=FIELD, sw=1.3, rx=3))
    els.append(text(X((Wns + bStart) / 2), byc + 30, "пізній старт", size=10, color=FIELD))

    # --- стрілка перетікання: той самий відрізок A→B ---
    els.append(line(X((Wns + logicA) / 2), ayc + 16, X((Wns + bStart) / 2), byc - 16,
                    color=INK, sw=1.4, dash="3 3"))
    els.append(text(X(Wns + 0.05), 250, "той самий відрізок: borrow_out(A) → borrow_in(B)",
                    size=11, color=INK, anchor="start", italic=True))

    # --- вертикальний пунктир W крізь обидві смуги (номінальна межа) ---
    els.append(line(X(Wns), ayc - 20, X(Wns), byc + 20, color=MUTED, sw=1.0, dash="2 3"))

    render(os.path.join(IMG, "borrow-budget.svg"), W, H, *els)


if __name__ == "__main__":
    fig_wall_vs_window()
    fig_borrow_across()
    fig_two_phase()
    fig_budget()
    fig_borrow_budget()
    print("figures written to", IMG)
