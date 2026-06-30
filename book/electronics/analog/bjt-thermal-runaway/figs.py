# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Три входи тепла в рівняння струму колектора BJT ──────────────────────
def fig_three_pushes():
    """Що в рівнянні Ic = β·Ib + (β+1)·ICBO сповзає від тепла:
    β росте, ICBO росте, VBE падає — усі три штовхають Ic в один бік."""
    W, H = 760, 380
    frags = []
    # центральне рівняння
    eqx, eqy = W / 2, 96
    eb, ew, eh = textbox(eqx, eqy, "Ic = β · Ib + (β + 1) · ICBO",
                         size=20, pad=16, stroke=INK, sw=2.2, bold=True, min_w=360)
    frags.append(eb)

    # три рамки-чинники під рівнянням
    items = [
        (W * 0.20, "β (підсилення)\nросте з T",      "+0.5…1 %/°C", POS),
        (W * 0.50, "VBE (відкривання)\nпадає з T",    "−2 мВ/°C",    POS),
        (W * 0.80, "ICBO (витік)\nросте з T",         "×2 / +10 °C", POS),
    ]
    boxes = []
    for (x, label, num, col) in items:
        b, w, h = textbox(x, 250, label, size=14, pad=12,
                          fill="#fdecea", stroke=col, sw=2.0, color=INK)
        frags.append(b)
        boxes.append((x, 250, w, h))
        nb, _, _ = textbox(x, 250 + h / 2 + 30, num, size=13, pad=8,
                           stroke=col, sw=1.6, color=col, bold=True)
        frags.append(nb)

    # стрілки від рівняння до кожного чинника
    for (x, y, w, h) in boxes:
        frags.append(arrow(eqx + (x - eqx) * 0.18, eqy + eh / 2 + 4,
                           x, y - h / 2 - 6, color=POS, sw=2.0))

    frags.append(text(W / 2, H - 18,
                      "усі три зсуви штовхають Ic в один бік — угору",
                      size=14, color=POS, italic=True, bold=True))
    render(os.path.join(IMG, "three-pushes.svg"), W, H, *frags,
           title="Три температурні зсуви в струмі колектора BJT")


# ── 2. Сходинка зміщень: чим краще тримає базу — тим менший S ───────────────
def fig_bias_ladder():
    """Три способи зміщення BJT і їхній чинник стійкості S = ΔIc/ΔICO:
    фіксований струм бази (S = β+1, погано) → з RE → подільник (S мале, добре)."""
    W, H = 760, 408
    frags = []
    rows = [
        ("Фіксований струм бази", "тільки резистор база→живлення",
         "S = β + 1", "≈ 150…300", POS, "#fdecea", "розгін легкий"),
        ("Емітерний резистор RE", "RE дає від'ємний зв'язок за струмом",
         "S = (β+1)·(1+RB/RE) / (1+β+RB/RE)", "≈ 10…30", MUTED, FILL, "помітно стійкіше"),
        ("Подільник + RE", "база жорстко зафіксована, RE гальмує",
         "S → (1 + RB/RE),  RB мале", "≈ 3…10", FIELD, "#eafaf0", "майже не пливе"),
    ]
    y = 78
    bw = W - 80
    bx = 40
    for (name, sub, sform, sval, col, fillc, verdict) in rows:
        bh = 86
        frags.append(rect(bx, y, bw, bh, fill=fillc, stroke=col, sw=2.0, rx=8))
        frags.append(text(bx + 18, y + 28, name, size=16, color=INK, anchor="start", bold=True))
        frags.append(text(bx + 18, y + 50, sub, size=12.5, color=MUTED, anchor="start"))
        frags.append(text(bx + 18, y + 72, sform, size=12.5, color=col, anchor="start", bold=True))
        # права колонка: значення S і вирок
        frags.append(text(bx + bw - 18, y + 34, sval, size=20, color=col, anchor="end", bold=True))
        frags.append(text(bx + bw - 18, y + 58, verdict, size=12.5, color=col, anchor="end", italic=True))
        y += bh + 14

    frags.append(text(W / 2, H - 14,
                      "що жорсткіше зафіксована база й сильніший RE — то менший S, то стійкіше",
                      size=12.5, color=FIELD, anchor="middle", italic=True))
    render(os.path.join(IMG, "bias-ladder.svg"), W, H, *frags,
           title="Чинник стійкості S за різних схем зміщення BJT")


# ── 3. Витік приходить у колектор помножений на (β+1) ───────────────────────
def fig_leakage_gain():
    """Крихітний ICBO у переході база–колектор виходить у колекторний струм
    помноженим на (β+1): транзистор підсилює власний паразитний витік."""
    W, H = 760, 320
    frags = []
    # ліворуч — джерело витоку (мала рамка)
    a, aw, ah = textbox(150, 150, "ICBO\nвитік переходу\nБ–К", size=14, pad=12,
                        stroke=POS, sw=2.0, color=INK, fill="#fdecea")
    frags.append(a)
    frags.append(text(150, 150 + ah / 2 + 26, "крихітний (нА)", size=12.5,
                      color=MUTED, italic=True))

    # посередині — «×(β+1)» транзистор
    m, mw, mh = textbox(W / 2, 150, "транзистор\n×(β + 1)", size=16, pad=16,
                        stroke=INK, sw=2.2, color=INK, bold=True)
    frags.append(m)

    # праворуч — наслідок у колекторі (велика рамка)
    c, cw, ch = textbox(W - 150, 150, "ICEO = (β+1)·ICBO\nдодаток до Ic", size=14, pad=12,
                        stroke=POS, sw=2.2, color=INK, fill="#fdecea")
    frags.append(c)
    frags.append(text(W - 150, 150 + ch / 2 + 26, "у сотні разів більший",
                      size=12.5, color=POS, italic=True, bold=True))

    # стрілки
    frags.append(arrow(150 + aw / 2 + 6, 150, W / 2 - mw / 2 - 8, 150, color=POS, sw=2.4))
    frags.append(arrow(W / 2 + mw / 2 + 6, 150, W - 150 - cw / 2 - 8, 150, color=POS, sw=2.6))

    frags.append(text(W / 2, H - 20,
                      "тепло множить ICBO — а схема ще раз множить його на (β+1)",
                      size=14, color=POS, italic=True))
    render(os.path.join(IMG, "leakage-gain.svg"), W, H, *frags,
           title="Власний витік, підсилений у (β+1) разів")


# ── 4. RE «бачиться» з боку бази помноженим на (β+1) ────────────────────────
def fig_re_reflected():
    """Чому RE входить у рівняння бази як (β+1)·RE: крізь резистор тече струм
    емітера (β+1)·Ib, тож база «бачить» падіння (β+1)·Ib·RE — наче опір більший."""
    W, H = 760, 360
    frags = []
    # вертикальна вісь кола: база зверху, емітер знизу, RE до землі
    cx = 250
    # вузол бази
    frags.append(circle(cx, 90, 7, fill=INK, stroke=INK, sw=1.5))
    frags.append(text(cx - 16, 94, "база", size=13, color=INK, anchor="end"))
    frags.append(text(cx + 16, 78, "Ib  →", size=13, color=NEG, anchor="start", bold=True))
    # транзистор (рамка) між базою та емітером
    tb, tw, th = textbox(cx, 165, "BJT", size=15, pad=14, stroke=INK, sw=2.0, bold=True)
    frags.append(tb)
    frags.append(line(cx, 97, cx, 165 - th / 2, color=INK, sw=2.0))
    # емітерний вузол
    frags.append(line(cx, 165 + th / 2, cx, 230, color=INK, sw=2.0))
    frags.append(circle(cx, 230, 7, fill=INK, stroke=INK, sw=1.5))
    frags.append(text(cx + 16, 226, "емітер", size=13, color=INK, anchor="start"))
    frags.append(text(cx + 20, 250, "Ie = (β+1)·Ib  ↓", size=13, color=POS, anchor="start", bold=True))
    # RE до землі
    frags.append(rect(cx - 16, 262, 32, 50, fill="#eafaf0", stroke=FIELD, sw=2.0, rx=4))
    frags.append(text(cx + 28, 290, "RE", size=14, color=FIELD, anchor="start", bold=True))
    frags.append(line(cx, 312, cx, 330, color=INK, sw=2.0))
    frags.append(line(cx - 18, 330, cx + 18, 330, color=INK, sw=2.5))  # земля
    frags.append(line(cx - 11, 336, cx + 11, 336, color=INK, sw=2.0))
    frags.append(line(cx - 4, 342, cx + 4, 342, color=INK, sw=1.6))

    # права колонка — висновок: падіння, віднесене до струму бази
    bx = 470
    e1, ew, eh = textbox(bx + 130, 120,
                         "падіння на RE\n= Ie · RE\n= (β+1)·Ib · RE",
                         size=14, pad=14, stroke=FIELD, sw=2.0, color=INK, fill="#eafaf0")
    frags.append(e1)
    e2, ew2, eh2 = textbox(bx + 130, 240,
                           "віднести до Ib  ⇒\nбаза «бачить» опір\n(β+1)·RE",
                           size=14, pad=14, stroke=INK, sw=2.2, color=INK, bold=True)
    frags.append(e2)
    frags.append(arrow(bx + 130, 120 + eh / 2 + 4, bx + 130, 240 - eh2 / 2 - 6,
                       color=INK, sw=2.0))
    # стрілка від кола до висновку
    frags.append(arrow(cx + 70, 200, bx + 130 - ew / 2 - 8, 130, color=MUTED, sw=1.8))

    frags.append(text(W / 2, H - 14,
                      "малий струм бази тече крізь RE як великий струм емітера — тому в колі бази RE «важить» у (β+1) разів",
                      size=12, color=FIELD, anchor="middle", italic=True))
    render(os.path.join(IMG, "re-reflected.svg"), W, H, *frags,
           title="Чому RE входить у коло бази як (β+1)·RE")


# ── 5. Три чинники стійкості складаються в повний дрейф струму ───────────────
def fig_three_factors():
    """Повний температурний дрейф ΔIc = S·ΔICO + S_VBE·ΔVBE + S_β·Δβ:
    три похідні від того самого рівняння кола, кожна множить свій поштовх."""
    W, H = 780, 380
    frags = []
    # три вхідні поштовхи (ліворуч)
    ins = [
        (90,  "ΔICO\nвитік ↑",   POS,  "#fdecea"),
        (170, "ΔVBE\nсповзання ↓", NEG, "#eaf0fd"),
        (250, "Δβ\nпідсилення ↑", POS,  "#fdecea"),
    ]
    facs = [
        (90,  "× S",     "= ΔIc/ΔICO"),
        (170, "× S_VBE", "= ΔIc/ΔVBE"),
        (250, "× S_β",   "= ΔIc/Δβ"),
    ]
    boxes = []
    for (y, lbl, col, fillc), (yf, fl, fsub) in zip(ins, facs):
        b, w, h = textbox(140, y, lbl, size=13, pad=10, stroke=col, sw=1.9,
                          color=INK, fill=fillc)
        frags.append(b)
        # множник
        fb, fw, fh = textbox(360, y, fl, size=15, pad=11, stroke=INK, sw=2.0,
                             color=INK, bold=True, min_w=92)
        frags.append(fb)
        frags.append(text(360, y + fh / 2 + 16, fsub, size=11, color=MUTED, italic=True))
        frags.append(arrow(140 + w / 2 + 6, y, 360 - fw / 2 - 8, y, color=col, sw=2.0))
        boxes.append((360, y, fw, fh))

    # сумовий вузол
    sumx = 560
    frags.append(circle(sumx, 170, 22, fill="#fff", stroke=INK, sw=2.2))
    frags.append(text(sumx, 178, "Σ", size=26, color=INK, bold=True))
    for (x, y, w, h) in boxes:
        frags.append(arrow(x + w / 2 + 6, y, sumx - 26, 170 + (y - 170) * 0.25,
                           color=MUTED, sw=1.8))

    # результат
    rb, rw, rh = textbox(700, 170, "ΔIc\nповний\nдрейф", size=15, pad=14,
                         stroke=POS, sw=2.4, color=INK, bold=True, fill="#fdecea")
    frags.append(rb)
    frags.append(arrow(sumx + 24, 170, 700 - rw / 2 - 8, 170, color=POS, sw=2.6))

    frags.append(text(W / 2, H - 16,
                      "ΔIc = S·ΔICO + S_VBE·ΔVBE + S_β·Δβ — три чутливості того самого кола, кожна множить свій поштовх",
                      size=12, color=INK, anchor="middle", italic=True))
    render(os.path.join(IMG, "three-factors.svg"), W, H, *frags,
           title="Повний дрейф струму: три чинники стійкості")


if __name__ == "__main__":
    fig_three_pushes()
    fig_bias_ladder()
    fig_leakage_gain()
    fig_re_reflected()
    fig_three_factors()
    print("ok: figures written to", IMG)
